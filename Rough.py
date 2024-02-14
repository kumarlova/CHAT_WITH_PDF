from flask import Flask, request, jsonify
import logging
from llama_index import download_loader
from pathlib import Path

app = Flask(__name__)

class AWS_S3_Loader:
    def __init__(self, bucket, key, aws_access_id, aws_access_secret):
        self.bucket = bucket
        self.key = key
        self.aws_access_id = aws_access_id
        self.aws_access_secret = aws_access_secret
        self.logger = logging.getLogger(__name__)  # Creating a logger instance

    def load(self):
        try:
            self.logger.info("AWS S3 loader")
            self.logger.info(f"Bucket: {self.bucket}, Key: {self.key}")
            file_extension = Path(self.key).suffix.lower()
            allowed_extensions = ['.txt', '.pdf', '.ppt', '.docx']
            if file_extension in allowed_extensions:
                S3Reader = download_loader("S3Reader")
                loader = S3Reader(bucket=self.bucket, key=self.key, aws_access_id=self.aws_access_id, aws_access_secret=self.aws_access_secret)
                documents = loader.load_data()
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")

            docs = []
            for doc in documents:
                # Modify the document as needed
                doc.metadata["source"] = f"s3://{self.bucket}/{self.key}"
                # Additional processing based on document type (if needed)
                docs.append(doc)

            self.logger.info("Successfully loaded file from S3 bucket")
            return docs
        except Exception as e:
            self.logger.error(f"Error loading file from S3 bucket: {e}")
            raise IOError(f"Error loading file from S3 bucket: {e}")

@app.route('/load_s3_document', methods=['POST'])
def load_s3_document():
    try:
        # Extract parameters from the request
        bucket = request.form.get('bucket')
        key = request.form.get('key')
        aws_access_id = request.form.get('aws_access_id')
        aws_access_secret = request.form.get('aws_access_secret')

        # Create an instance of AWS_S3_Loader
        loader = AWS_S3_Loader(bucket=bucket, key=key, aws_access_id=aws_access_id, aws_access_secret=aws_access_secret)

        # Load documents from the specified S3 bucket and key
        documents = loader.load()

        # Return the documents as JSON response
        return jsonify(documents)
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(level=logging.INFO)  # Set logging level to INFO
    app.run(host='0.0.0.0', port=5000)  # Run the Flask app on your cloud machine
