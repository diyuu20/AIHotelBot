# Document Classification Integration

This document explains how to integrate and use the YOLO-based document classification feature in the AI Hotel Bot system.

## Overview

The document classification system validates uploaded document images to ensure they match the expected document type before processing them with OCR. This prevents users from uploading incorrect documents and improves the overall verification process.

## Features

- **YOLO-based Classification**: Uses YOLO model to classify document types
- **Supported Document Types**: Aadhaar Card, Passport, Driving Licence
- **Real-time Validation**: Validates documents before OCR processing
- **User-friendly Feedback**: Provides clear instructions and validation messages
- **Configurable Thresholds**: Adjustable confidence thresholds for validation

## Supported Document Classes

The system recognizes the following document classes:

- `aadhar_front` - Aadhaar card front side
- `aadhar_back` - Aadhaar card back side
- `driving_license_front` - Driving licence front side
- `driving_license_back` - Driving licence back side
- `passport` - Passport document
- `pan_card_front` - PAN card front (not currently used in UI)
- `voter_id` - Voter ID (not currently used in UI)

## Setup Instructions

### 1. Install Dependencies

Make sure you have the required dependencies installed:

```bash
pip install ultralytics torch torchvision
```

### 2. Configure YOLO Model

1. **Train your YOLO model** with the document classes listed above
2. **Update the configuration** in `config.py`:

```python
# Set the path to your trained YOLO model
YOLO_MODEL_PATH = "path/to/your/document_classifier.pt"

# Adjust confidence threshold if needed
DOCUMENT_VALIDATION_CONFIDENCE_THRESHOLD = 0.5
```

### 3. Test the Integration

Run the test script to verify everything is working:

```bash
python test_document_classifier.py
```

## How It Works

### 1. Document Upload Flow

1. User selects document type (Aadhaar, Passport, or Driving Licence)
2. User uploads or captures document image
3. System validates document type using YOLO classification
4. If validation passes, document proceeds to OCR processing
5. If validation fails, user receives error message and can try again

### 2. Validation Process

```python
# The validation process checks:
validation_result = validate_document_type(
    image_path="path/to/document.jpg",
    expected_doc_type="aadhaar",  # or "passport", "driving_licence"
    confidence_threshold=0.5
)

# Returns:
{
    "valid": True/False,
    "predicted_class": "aadhar_front",
    "confidence": 0.85,
    "expected_type": "aadhaar",
    "message": "Document validated as aadhar_front with 85% confidence"
}
```

### 3. User Interface Updates

The document upload page now includes:

- **Document Type Instructions**: Dynamic instructions based on selected document type
- **Validation Feedback**: Real-time feedback on document validation
- **Error Handling**: Clear error messages for invalid documents

## Configuration Options

### Model Configuration

```python
# config.py
YOLO_MODEL_PATH = "models/document_classifier.pt"  # Path to your YOLO model
DOCUMENT_VALIDATION_CONFIDENCE_THRESHOLD = 0.5    # Confidence threshold
```

### Document Type Mapping

The system maps user-friendly document types to YOLO classes:

```python
doc_type_mapping = {
    'aadhaar': ['aadhar_front', 'aadhar_back'],
    'passport': ['passport'],
    'driving_licence': ['driving_license_front', 'driving_license_back']
}
```

## Troubleshooting

### Common Issues

1. **Model Not Found**
   - Ensure `YOLO_MODEL_PATH` is correctly set in `config.py`
   - Check that the model file exists and is accessible

2. **Low Confidence Scores**
   - Adjust `DOCUMENT_VALIDATION_CONFIDENCE_THRESHOLD` in `config.py`
   - Ensure document images are clear and well-lit
   - Consider retraining the model with more diverse data

3. **Classification Errors**
   - Verify that your YOLO model was trained with the correct class names
   - Check that the model output format matches the expected format

### Debug Mode

Enable debug output by adding print statements in `document_classifier.py`:

```python
# Add this to see detailed classification results
print(f"Classification result: {classification_result}")
```

## Integration Points

### Main Application (`app.py`)

The document validation is integrated into the `/document_verification/<booking_id>/<guest_name>` route:

```python
# Validate document type before OCR processing
validation_result = validate_document_type(filepath, doc_type, confidence_threshold=0.5)

if not validation_result.get('valid', False):
    # Show error message and return to upload page
    flash(f"Document validation failed: {validation_result.get('message')}", "error")
    return render_template('document_upload.html', ...)
```

### Frontend Template (`templates/document_upload.html`)

The template includes:

- Dynamic document type instructions
- Validation status display
- Enhanced user feedback

## Future Enhancements

1. **Additional Document Types**: Support for PAN card, Voter ID
2. **Batch Processing**: Validate multiple documents at once
3. **Advanced Validation**: Check document authenticity and quality
4. **Analytics**: Track validation success rates and common errors

## Support

For issues or questions regarding the document classification feature:

1. Check the test script output: `python test_document_classifier.py`
2. Verify model configuration in `config.py`
3. Review the validation logs in the application console
4. Ensure all dependencies are properly installed



