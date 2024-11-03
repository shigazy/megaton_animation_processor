import os
import logging
import shutil
from fbx_loader import load_fbx_animation
from blender_renderer import render_animation
from gif_generator import create_gif, convert_to_webp
from grid_generator import create_8k_grid
import tkinter as tk
from tkinter import filedialog
import json
from datetime import datetime
import boto3
import requests
import mysql.connector
import traceback
import random
import uuid
from urllib import request, parse
import threading
import queue
import time
import configparser
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from move_gif import move_gifs_to_subfolder
from openai_parser import describe_animation, get_animation_length, create_json_file

logging.basicConfig(level=logging.DEBUG)  # Changed to DEBUG for more detailed logs
logger = logging.getLogger(__name__)

def get_aws_credentials():
    config = configparser.ConfigParser()
    credentials_path = os.path.expanduser("~/.aws/credentials.txt")
    #print(f"Attempting to read credentials from: {credentials_path}")
    config.read(credentials_path)
    
    if 'default' in config:
        #print("Found 'default' section in credentials file")
        return {
            'aws_access_key_id': config['default'].get('aws_access_key_id'),
            'aws_secret_access_key': config['default'].get('aws_secret_access_key')
        }
    else:
        print("'default' section not found in credentials file")
        print(f"Sections found: {config.sections()}")
    return {}

def get_aws_config():
    config = configparser.ConfigParser()
    config_path = os.path.expanduser("~/.aws/config.txt")
    #print(f"Attempting to read config from: {config_path}")
    config.read(config_path)
    
    if 'default' in config:
        #print("Found 'default' section in config file")
        return {
            'region': config['default'].get('region', 'us-east-1')
        }
    else:
        print("'default' section not found in config file")
        print(f"Sections found: {config.sections()}")
    return {'region': 'us-east-1'}

def get_secret(secret_name):
    credentials = get_aws_credentials()
    config = get_aws_config()
    region_name = config['region']
    
    #print(f"Credentials: {credentials}")
    #print(f"Config: {config}")
    #print(f"Creating boto3 client with region: {region_name}")
    client = boto3.client(
        'secretsmanager',
        aws_access_key_id=credentials.get('aws_access_key_id'),
        aws_secret_access_key=credentials.get('aws_secret_access_key'),
        region_name=region_name
    )
    #print("Client created successfully")
    
    try:
       # print(f"Attempting to get secret value for: {secret_name}")
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        #print("Secret value retrieved successfully")
        if 'SecretString' in get_secret_value_response:
            return json.loads(get_secret_value_response['SecretString'])
        else:
            raise ValueError("Secret is not a string")
    except Exception as e:
        print(f"Error retrieving secret: {str(e)}")
        return None

def list_tables_and_structure(connection):
    cursor = connection.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    for table in tables:
        if table[0] == 'api_uploads':
            cursor.execute(f"DESCRIBE {table[0]}")
            structure = cursor.fetchall()
    cursor.close()

def upload_to_s3(local_path, s3_folder):
    try:
        credentials = get_aws_credentials()
        config = get_aws_config()
        region_name = config['region']
        
        print(f"Creating S3 client with region: {region_name}")
        s3 = boto3.client('s3',
            aws_access_key_id=credentials.get('aws_access_key_id'),
            aws_secret_access_key=credentials.get('aws_secret_access_key'),
            region_name=region_name
        )
        bucket_name = 'megaton-storage'
        
        file_name = os.path.basename(local_path)
        s3_key = f"{s3_folder}/{file_name}"
        
        print(f"Uploading file {file_name} to S3 bucket {bucket_name}")
        s3.upload_file(local_path, bucket_name, s3_key)
        
        s3_url = f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"
        print(f"File uploaded successfully to {s3_url}")
        return s3_url
    except Exception as e:
        print(f"Error uploading to S3: {str(e)}")
        return None

def connect_to_rds():
    secret_name = 'arn:aws:secretsmanager:us-east-1:035700659240:secret:rds!db-db12e38f-e948-4dd0-8cb5-6c599e31ae53-jEabKN'
    db_credentials = get_secret(secret_name)
    
    if db_credentials:
        try:
            conn = mysql.connector.connect(
                host='database-1.c9e2eoe0qp8t.us-east-1.rds.amazonaws.com',
                database='megaton',
                user=db_credentials['username'],
                password=db_credentials['password'],
                port='3306'
            )
            return conn
        except mysql.connector.Error as err:
            print(f"Error connecting to RDS: {err}")
            return None
    else:
        print("Failed to retrieve database credentials")
        return None

def process_animation(fbx_file, output_dir):
    try:
        logger.debug(f"Attempting to process: {fbx_file}")
        # Check if the FBX file exists
        if not os.path.exists(fbx_file):
            raise FileNotFoundError(f"FBX file not found: {fbx_file}")

        logger.debug(f"File exists: {fbx_file}")
        
        # Copy FBX file to output directory
        fbx_filename = os.path.basename(fbx_file)
        fbx_output_path = os.path.join(output_dir, fbx_filename)
        shutil.copy2(fbx_file, fbx_output_path)
        logger.debug(f"Copied FBX file to: {fbx_output_path}")
        
        # Load FBX animation
        animation = load_fbx_animation(fbx_file)
        
        # Render animation frames
        frames, temp_dir = render_animation(fbx_file, animation, output_dir)
        
        # Check if frames were actually rendered
        existing_frames = [f for f in frames if os.path.exists(f)]
        if not existing_frames:
            raise Exception("No frames were rendered")
        
        # Generate GIF
        base_name = os.path.splitext(os.path.basename(fbx_file))[0]
        gif_path = os.path.join(output_dir, f"{base_name}.gif")
        create_gif(existing_frames, gif_path)
        
        # Convert GIF to WebP
        webp_path = os.path.join(output_dir, f"{base_name}.webp")
        convert_to_webp(gif_path, webp_path)
        
        # Create 8K grid
        grid_path = os.path.join(output_dir, f"{base_name}_grid.png")
        create_8k_grid(existing_frames, grid_path)
        
        logger.info(f"Processed {fbx_file} successfully")
        
        # Run OpenAI parser on the grid image
        try:
            base_name, description, action_prompt, brief_action = describe_animation(grid_path)
            frame_count, duration_seconds, frame_rate = get_animation_length(fbx_output_path)
            
            # Create JSON file
            create_json_file(
                base_name, 
                description, 
                action_prompt, 
                brief_action,
                {
                    "frame_count": frame_count,
                    "duration_seconds": duration_seconds,
                    "frame_rate": frame_rate
                },
                output_dir
            )
            logger.info(f"Created JSON metadata for {base_name}")
        except Exception as e:
            logger.error(f"Error creating metadata: {str(e)}")
        
        # Clean up temporary directory
        shutil.rmtree(temp_dir)
        
    except FileNotFoundError as e:
        logger.error(str(e))
    except Exception as e:
        logger.error(f"Error processing {fbx_file}: {str(e)}")

def get_unique_dated_folder(output_dir):
    today = datetime.now().strftime('%m-%d-%Y')
    base_folder = os.path.join(output_dir, today)
    
    if not os.path.exists(base_folder):
        return base_folder
    
    # Check for existing numbered folders
    counter = 1
    while True:
        numbered_folder = f"{base_folder}_{counter:03d}"  # This creates 001, 002, etc.
        if not os.path.exists(numbered_folder):
            return numbered_folder
        counter += 1

def upload_batch_to_s3_and_record(output_dir):
    try:
        # Get unique dated folder path
        dated_output_dir = get_unique_dated_folder(output_dir)
        os.makedirs(dated_output_dir, exist_ok=True)
        
        logger.debug(f"Created output directory: {dated_output_dir}")
        
        # Move all files from output_dir to dated subfolder
        files = os.listdir(output_dir)
        uploaded_urls = []
        
        for file in files:
            src_path = os.path.join(output_dir, file)
            if os.path.isfile(src_path):  # Make sure it's a file, not directory
                # Move file to dated subfolder
                dst_path = os.path.join(dated_output_dir, file)
                shutil.move(src_path, dst_path)
                
                # Upload from new location
                s3_url = upload_to_s3(dst_path, 'animations')
                if s3_url:
                    uploaded_urls.append(s3_url)
                    logger.debug(f"Successfully uploaded: {s3_url}")
                else:
                    logger.error(f"Failed to upload: {file}")
        
        # Prepare data for database
        upload_data = {
            'urls': uploaded_urls,
            'status': 'uploaded',
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Connect to database and insert record
        conn = connect_to_rds()
        if conn:
            try:
                cursor = conn.cursor()
                # Generate a proper UUID
                new_uuid = str(uuid.uuid4())
                sql = "INSERT INTO api_uploads (id, data) VALUES (%s, %s)"
                json_data = json.dumps(upload_data)
                cursor.execute(sql, (new_uuid, json_data))
                conn.commit()
                logger.info(f"Successfully recorded upload with ID: {new_uuid}")
            except Exception as e:
                logger.error(f"Database error: {str(e)}")
                logger.error(traceback.format_exc())
            finally:
                cursor.close()
                conn.close()
        
        return uploaded_urls
    except Exception as e:
        logger.error(f"Error in batch upload: {str(e)}")
        logger.error(traceback.format_exc())
        return []

def main():
    # Create root window but hide it
    root = tk.Tk()
    root.withdraw()

    # Ask user to select input directory
    fbx_dir = filedialog.askdirectory(title="Select FBX Input Directory")
    if not fbx_dir:  # User cancelled
        print("No input directory selected. Exiting...")
        return

    # Ask user to select output directory
    output_dir = filedialog.askdirectory(title="Select Output Directory")
    if not output_dir:  # User cancelled
        print("No output directory selected. Exiting...")
        return

    logger.debug(f"FBX directory: {fbx_dir}")
    logger.debug(f"Output directory: {output_dir}")

    os.makedirs(output_dir, exist_ok=True)
    
    # Check if the FBX directory exists
    if not os.path.exists(fbx_dir):
        logger.error(f"FBX directory not found: {fbx_dir}")
        return

    # List all files in the directory
    all_files = os.listdir(fbx_dir)
    logger.debug(f"All files in directory: {all_files}")

    fbx_files = [f for f in all_files if f.lower().endswith(".fbx")]
    
    if not fbx_files:
        logger.warning(f"No FBX files found in {fbx_dir}")
        return

    logger.debug(f"FBX files found: {fbx_files}")

    for fbx_file in fbx_files:
        full_path = os.path.join(fbx_dir, fbx_file)
        logger.debug(f"Processing file: {full_path}")
        process_animation(full_path, output_dir)

    # After processing all animations, move GIFs to subfolder
    move_gifs_to_subfolder(output_dir)
    print("All GIF files have been moved to the GIF subfolder.")

    # After processing all animations and moving GIFs
    logger.info("Starting S3 upload process")
    uploaded_urls = upload_batch_to_s3_and_record(output_dir)
    
    if uploaded_urls:
        logger.info(f"Successfully uploaded {len(uploaded_urls)} files")
        logger.debug(f"Uploaded URLs: {uploaded_urls}")
    else:
        logger.error("No files were uploaded successfully")

if __name__ == "__main__":
    main()