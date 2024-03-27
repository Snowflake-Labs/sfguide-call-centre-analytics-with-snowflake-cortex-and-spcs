#!/bin/bash
HUGGING_FACE_MODEL=NumbersStation/nsql-llama-2-7B

# Check if HUGGING_FACE_MODEL is set
if [ -z "${HUGGING_FACE_MODEL}" ]; then
    echo "Error: HUGGING_FACE_MODEL not set"
    exit 1
fi

# Extract org and repo from HUGGING_FACE_MODEL
HF_ORG=$(echo $HUGGING_FACE_MODEL | cut -d'/' -f1)
HF_REPO=$(echo $HUGGING_FACE_MODEL | cut -d'/' -f2)

check_for_model() {
  set -e  # Exit on command errors
  set -x  # Print each command before execution, useful for debugging

  TARGET_DIR="/notebooks/llm-workspace/$HF_REPO"

  # Check if the target directory exists
  if [ -d "$TARGET_DIR" ]; then
      echo "Model appears to exist in stage. Skipping download..."
  else
      git lfs install
      # Create a temporary directory
      TEMP_DIR=$(mktemp -d)
      echo "\n\n"
      echo "The provided model does not exist in the stage."
      echo "This startup script will download it for you and save to stage. This can take a few minutes."
      echo "This will not need to download on future startups."
      echo "\n\n"
      echo "Cloning the repository into temporary directory..."
      # Clone the repository into the temporary directory
      GIT_TRACE=1 git clone --depth 1 https://huggingface.co/$HF_ORG/$HF_REPO $TEMP_DIR
      cd "$TEMP_DIR"

      echo "Copying contents to model stage..."
      # Copy contents of the temporary directory to TARGET_DIR
      rsync -a --exclude=".git" "$TEMP_DIR/" "$TARGET_DIR/"

      # Clean up temporary directory
      rm -rf "$TEMP_DIR"
  fi

  # Remove the temporary credentials.
  # rm /tmp/git-credentials
}


check_for_model


# wait indefinitely

