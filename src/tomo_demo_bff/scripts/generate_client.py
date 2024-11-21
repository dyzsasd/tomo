import subprocess
import json
import os
from pathlib import Path
import requests


def generate_typescript_client(openapi_url: str, output_dir: str):
    """Generate TypeScript client from OpenAPI specification"""

    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Download OpenAPI spec
    response = requests.get(openapi_url)
    spec = response.json()

    # Save spec to temporary file
    spec_file = "temp_openapi.json"
    with open(spec_file, "w") as f:
        json.dump(spec, f)

    try:
        # Generate client using openapi-generator
        subprocess.run(
            [
                "openapi-generator-cli",
                "generate",
                "-i",
                spec_file,
                "-g",
                "typescript-fetch",
                "-o",
                output_dir,
                "--additional-properties=",
                "supportsES6=true,"
                "npmName=@tomo/client,"
                "npmVersion=1.0.0,"
                "withInterfaces=true,"
                "typescriptThreePlus=true",
            ],
            check=True,
        )

        # Clean up temporary files
        if os.path.exists(spec_file):
            os.remove(spec_file)

        print(f"TypeScript client generated successfully in {output_dir}")

    except subprocess.CalledProcessError as e:
        print(f"Error generating TypeScript client: {e}")
        raise
    finally:
        # Ensure cleanup
        if os.path.exists(spec_file):
            os.remove(spec_file)


if __name__ == "__main__":
    # URL of your running FastAPI service
    OPENAPI_URL = "http://localhost:8000/api/v1/openapi.json"
    # Output directory for generated client
    OUTPUT_DIR = "generated/typescript-client"

    generate_typescript_client(OPENAPI_URL, OUTPUT_DIR)
