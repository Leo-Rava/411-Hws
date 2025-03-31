#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5000/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done


###############################################
#
# Health checks
#
###############################################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

# Function to check the database connection
check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}


##########################################################
#
# Song Management
#
##########################################################

add_boxer() {
  name=$1
  weight=$2
  height=$3
  reach=$4
  age=$5

  echo "Adding boxer ($artist - $title, $year) to the ring..."
  curl -s -X POST "$BASE_URL/create-boxer" -H "Content-Type: application/json" \
    -d "{\"name\":\"$name\", \"weight\":\"$weight\", \"height\":$height, \"reach\":\"$reach\", \"age\":$age}" | grep -q '"status": "success"'

  if [ $? -eq 0 ]; then
    echo "Boxer added successfully."
  else
    echo "Failed to add Boxer."
    exit 1
  fi
}

delete_boxer() {
  boxer_id=$1

  echo "Deleting boxer by ID ($boxer_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-boxer/$boxer_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer deleted successfully by ID ($boxer_id)."
  else
    echo "Failed to delete boxer by ID ($boxer_id)."
    exit 1
  fi
}

get_boxer_by_id() {
  boxer_id=$1

  echo "Getting song by ID ($boxer_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-boxer-by-id/$boxer_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer retrieved successfully by ID ($boxer_id)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Song JSON (ID $boxer_id):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get boxer by ID ($boxer_id)."
    exit 1
  fi
}

get_boxer_by_name() {
  name=$1

  echo "Getting boxer by name (Name: $name)..."
  response=$(curl -s -X GET "$BASE_URL/get-boxer-by-name/$boxer_name")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer retrieved successfully by name."
    if [ "$ECHO_JSON" = true ]; then
      echo "Boxer JSON (by name):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get boxer by name key."
    exit 1
  fi
}

############################################################
#
# Ring Management
#
############################################################

enter_ring() {
  boxer=$1

  echo "Adding boxer to ring: $boxer..."
  response=$(curl -s -X POST "$BASE_URL/enter-ring" \
    -H "Content-Type: application/json" \
    -d "{\"artist\":\"$boxer\"}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "boxer added to playlist successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Boxer JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to add boxer to ring."
    exit 1
  fi
}


clear_boxers() {
  echo "Clearing ring..."
  response=$(curl -s -X POST "$BASE_URL/clear-boxers")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Playlist cleared successfully."
  else
    echo "Failed to clear playlist."
    exit 1
  fi
}


############################################################
#
# Play Playlist
#
############################################################


get_boxers() {
  echo "Retrieving all boxers from ring..."
  response=$(curl -s -X GET "$BASE_URL/get-boxers")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "All boxers retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Songs JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve all boxers from ring."
    exit 1
  fi
}

# Function to play the rest of the playlist
bout() {
  echo "initiating fight between boxers in the ring..."
  curl -s -X POST "$BASE_URL/fight" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Boxers fought played successfully."
  else
    echo "Failed to fight boxers in ring."
    exit 1
  fi
}

######################################################
#
# Leaderboard
#
######################################################

# Function to get the song leaderboard sorted by play count
get_leaderboard() {
  echo "Getting boxer leaderboard sorted by win count..."
  response=$(curl -s -X GET "$BASE_URL/boxer-leaderboard?sort=win_count")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxing leaderboard retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Leaderboard JSON (sorted by win count):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get boxing leaderboard."
    exit 1
  fi
}

# Initialize the database
sqlite3 db/boxer.db < sql/init_db.sql

# Health checks
check_health
check_db

# Create songs
create_boxer "Josh" 165 54 3.4 32
create_boxer "Bob" 180 72 3.9 24
create_boxer "Jebedia" 200 78 4.1 19
create_boxer "Queen" 130 60 2.6 37
create_boxer "Donna" 190 40 4 40

delete_boxer 1

get_boxer_by_id 2
get_boxer_by_name "Bob"

get_leaderboard

enter_ring "Jebedia" 200 78 4.1 19
enter_ring "Queen" 130 60 2.6 37 

get_boxers

bout

clear_boxers