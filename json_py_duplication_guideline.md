# JSON Python Duplication Guideline

## Overview
This guide provides a comprehensive, step-by-step process for creating pipeline duplication files that read JSON output from a previous stage, independently extract all fields, and produce identical structure output to their own independent JSON file while maintaining proper pipeline integration.

---

## What This Process Accomplishes

### Core Functionality
1. **Pipeline Integration**: New file follows standard pipeline calling procedure
2. **Sequential Processing**: Waits for previous file to complete its task and logging
3. **Independent Field Extraction**: Uses its own coding logic to individually identify and extract every field from source JSON
4. **Identical Structure Output**: Produces output with exact same field names and structure as source
5. **Independent Logging**: Writes extracted data to its own dedicated JSON file with separate logging system

### Technical Implementation
- **Source**: Reads from previous pipeline stage's JSON output
- **Processing**: Field-by-field independent extraction (no copy/paste operations)
- **Output**: Writes to new independent JSON file with identical structure
- **Integration**: Called automatically by previous pipeline stage after completion

---

## Step-by-Step Implementation Guide

### Step 1: File Structure Setup

#### 1.1 Create New Python File
```
{previous_stage_name}_duplication.py
```

#### 1.2 Set Up Directory Structure
```
logs/{new_stage_name}/
└── {new_stage_name}.json
```

#### 1.3 File Path Template
```python
# Source file path (reads from previous stage)
source_file = '/path/to/logs/{previous_stage_name}/{previous_stage_name}.json'

# Output file path (writes to new stage)
output_file = '/path/to/logs/{new_stage_name}/{new_stage_name}.json'
```

---

### Step 2: File Header Documentation

```python
#!/usr/bin/env python3

"""
=============================================================================
{UPPERCASE_FILENAME}.PY - INDEPENDENT FIELD EXTRACTION & LOGGING
=============================================================================

# ========================================
# PIPELINE CALLING STANDARD - {UPPERCASE_FILENAME}.PY
# ========================================
# POSITION: {previous_stage}.py → {current_stage}.py [TERMINAL/CONTINUES]
# CALLS NEXT: {next_stage}.py OR None - depending on pipeline position
# PATTERN: Standard pipeline pattern with/without trigger_next_stage() function
# ========================================

PIPELINE POSITION:
{stage1}.py → {stage2}.py → ... → {previous_stage}.py → **{CURRENT_STAGE}.PY** → {next_stage}.py

TRIGGER/INITIATION:
- Automatically called by {previous_stage}.py after successful completion
- Triggered via: subprocess.run(['python3', '{current_stage}.py'], check=True)
- Follows standard pipeline calling pattern

PURPOSE:
This module INDEPENDENTLY processes the output of {previous_stage}.py by:
1. Reading from {previous_stage}.json (NOT copying or mirroring)
2. IDENTIFYING and EXTRACTING each individual field from the JSON structure
3. Creating its own independent conversion and analysis
4. Logging results to its own independent {current_stage}.json file

INDEPENDENT FIELD EXTRACTION:
- Each JSON field is individually identified and extracted
- No copy/paste or mirroring operations
- Independent processing logic for each data type
- Separate logging system with its own file paths

OUTPUT:
- File: /path/to/logs/{current_stage}/{current_stage}.json
- Independent logging system
- Field-by-field extraction results
=============================================================================
"""
```

---

### Step 3: Required Imports

```python
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
import pytz
```

---

### Step 4: Core Functions Implementation

#### 4.1 Data Loading Function
```python
def load_{previous_stage}_data() -> Optional[Dict[str, Any]]:
    """Load {previous_stage}.json data independently"""
    source_file = '/path/to/logs/{previous_stage}/{previous_stage}.json'
    
    try:
        if os.path.exists(source_file):
            with open(source_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print(f"ERROR: {previous_stage} source file not found: {source_file}")
            return None
    except Exception as e:
        print(f"ERROR: Failed to load {previous_stage} data: {e}")
        return None
```

#### 4.2 Field Extraction Function Template
```python
def extract_record_fields(record: Dict[str, Any]) -> Dict[str, Any]:
    """Extract fields using IDENTICAL structure as {previous_stage}.json"""
    
    extracted = {}
    
    # Extract basic fields with IDENTICAL field names
    basic_fields = ["field1", "field2", "field3"]  # Replace with actual field names
    for field in basic_fields:
        if field in record:
            extracted[field] = record[field]
    
    # Extract nested objects with IDENTICAL structure
    nested_objects = ["nested_obj1", "nested_obj2"]  # Replace with actual nested objects
    for obj_name in nested_objects:
        if obj_name in record:
            source_obj = record[obj_name]
            extracted[obj_name] = {}
            
            # Extract sub-fields within nested object
            for sub_field, sub_value in source_obj.items():
                extracted[obj_name][sub_field] = sub_value
    
    # Extract array fields with IDENTICAL structure
    array_fields = ["array_field1", "array_field2"]  # Replace with actual array fields
    for array_field in array_fields:
        if array_field in record:
            source_array = record[array_field]
            extracted[array_field] = []
            
            for item in source_array:
                extracted_item = {}
                # Extract each field within array items
                for item_field, item_value in item.items():
                    extracted_item[item_field] = item_value
                extracted[array_field].append(extracted_item)
    
    # Extract complex nested structures (like odds, environment, etc.)
    complex_fields = ["complex_field1", "complex_field2"]  # Replace with actual complex fields
    for complex_field in complex_fields:
        if complex_field in record:
            source_complex = record[complex_field]
            extracted[complex_field] = {}
            
            # Handle multi-level nesting
            for key, value in source_complex.items():
                extracted[complex_field][key] = value
    
    return extracted
```

#### 4.3 Output Creation Function
```python
def create_{current_stage}_output(source_data: Dict[str, Any], converted_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create {current_stage} output with IDENTICAL structure as {previous_stage}.json"""
    
    # Get current timezone (adjust as needed)
    tz = pytz.timezone('US/Eastern')
    current_time = datetime.now(tz)
    
    # Create output with IDENTICAL structure to {previous_stage}.json
    output_data = {
        "{metadata_section_name}": {  # Keep same metadata section name as source
            "generated_at": current_time.isoformat(),
            "generated_at_readable": current_time.strftime('%m/%d/%Y %I:%M:%S %p %Z'),
            "total_records": len(converted_records),  # Adjust field name as needed
            "source_file": "{previous_stage}.json",
            "version": "1.0"
        },
        "{main_data_section}": converted_records,  # Keep same main data section name as source
        "footer_completion": f"--- {current_stage} completed: {current_time.strftime('%m/%d/%Y %I:%M:%S %p %Z')} ---"
    }
    
    return output_data
```

#### 4.4 Data Saving Function
```python
def save_{current_stage}_data(output_data: Dict[str, Any]) -> bool:
    """Save {current_stage} data to independent {current_stage}.json file"""
    
    # Independent output file path
    output_file = '/path/to/logs/{current_stage}/{current_stage}.json'
    output_dir = os.path.dirname(output_file)
    
    # Create independent output directory
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created independent directory: {output_dir}")
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Independent {current_stage} data saved to: {output_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error saving independent {current_stage} data: {e}")
        return False
```

---

### Step 5: Main Processing Function

```python
def main():
    """Main independent field extraction and conversion process"""
    
    print(f"🔄 Starting independent field extraction from {previous_stage}.json...")
    
    # Load source data independently
    source_data = load_{previous_stage}_data()
    if not source_data:
        print(f"❌ Failed to load source data for independent processing")
        return 1
    
    # Extract main data list independently
    source_records = source_data.get("{main_data_section}", [])  # Adjust section name
    if not source_records:
        print(f"❌ No records found in source data for extraction")
        return 1
    
    print(f"📊 Processing {len(source_records)} records with IDENTICAL field structure...")
    
    # Process each record using IDENTICAL structure
    converted_records = []
    for i, record in enumerate(source_records, 1):
        print(f"   Extracting fields from record {i}/{len(source_records)}: {record.get('identifier_field', 'UNKNOWN')}")
        converted_record = extract_record_fields(record)
        converted_records.append(converted_record)
    
    # Create IDENTICAL output structure
    output_data = create_{current_stage}_output(source_data, converted_records)
    
    # Save to independent file
    success = save_{current_stage}_data(output_data)
    
    if success:
        print(f"✅ Independent field extraction completed with IDENTICAL structure")
        print(f"📁 Output: /path/to/logs/{current_stage}/{current_stage}.json")
        return 0
    else:
        print(f"❌ Independent field extraction failed")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
```

---

### Step 6: Pipeline Integration

#### 6.1 Modify Previous Stage File
Add this function to the previous stage file (e.g., `{previous_stage}.py`):

```python
def trigger_next_stage():
    """Call {current_stage} stage"""
    print(f"\n🎨 Calling {current_stage}.py for final processing...")
    
    try:
        subprocess.run(['python3', '{current_stage}.py'], check=True)
        print(f"✅ {current_stage} completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running {current_stage}.py: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error with {current_stage}.py: {e}")
        return 1
    
    return 0
```

#### 6.2 Update Previous Stage Main Function
Modify the main() function in the previous stage to call the new stage:

```python
def main():
    """Main entry point"""
    success = process_{previous_stage}()
    if success:
        exit_code = trigger_next_stage()  # Add this line
        return exit_code
    else:
        return 1
```

---

## Implementation Checklist

### Pre-Implementation
- [ ] Identify source file path and structure
- [ ] Determine output file path and directory structure
- [ ] Analyze source JSON to identify all field types (basic, nested, arrays, complex)
- [ ] Choose appropriate timezone for timestamps
- [ ] Determine if this is terminal stage or continues pipeline

### File Creation
- [ ] Create new Python file with appropriate naming convention
- [ ] Add comprehensive header documentation with pipeline position
- [ ] Import required dependencies
- [ ] Create output directory structure

### Core Function Implementation
- [ ] Implement data loading function with proper error handling
- [ ] Create field extraction function with IDENTICAL structure preservation
- [ ] Build output creation function with proper metadata
- [ ] Implement data saving function with independent file paths
- [ ] Create main processing function with proper logging

### Field Extraction Implementation
- [ ] Identify and extract ALL basic fields individually
- [ ] Handle ALL nested objects with identical structure
- [ ] Process ALL array fields with proper iteration
- [ ] Extract ALL complex nested structures
- [ ] Ensure NO copy/paste operations (individual field identification)

### Pipeline Integration
- [ ] Add trigger function to previous stage file
- [ ] Update previous stage main() to call new stage
- [ ] Test pipeline integration end-to-end
- [ ] Verify proper sequential execution

### Testing and Validation
- [ ] Run comprehensive field comparison test
- [ ] Verify 100% field coverage across all records
- [ ] Confirm identical structure preservation
- [ ] Test independent logging functionality
- [ ] Validate pipeline integration works correctly

---

## Directory Structure Template

```
project_root/
├── {previous_stage}.py
├── {current_stage}.py
└── logs/
    ├── {previous_stage}/
    │   └── {previous_stage}.json
    └── {current_stage}/
        └── {current_stage}.json
```

---

## Error Handling Best Practices

1. **File Not Found**: Always check if source file exists before reading
2. **Invalid JSON**: Use try/catch blocks for JSON parsing
3. **Missing Fields**: Use `.get()` method with defaults for optional fields
4. **Directory Creation**: Create output directories if they don't exist
5. **Pipeline Failures**: Return appropriate exit codes for pipeline management

---

## Key Success Criteria

✅ **Complete Field Coverage**: Every field from source JSON is individually identified and extracted  
✅ **Identical Structure**: Output maintains exact same field names and nesting as source  
✅ **Independent Processing**: No copy/paste operations - each field explicitly handled  
✅ **Pipeline Integration**: Follows standard calling procedure and sequential execution  
✅ **Independent Logging**: Separate file paths and logging system  
✅ **Error Handling**: Proper exception handling and exit codes  
✅ **Documentation**: Comprehensive header documentation and comments  

---

## Example Use Cases

- **Data Validation**: Create validation stage that independently verifies previous stage output
- **Format Conversion**: Transform data while maintaining identical structure
- **Audit Trail**: Create audit copies with independent processing logic
- **Quality Assurance**: Build QA stages that validate field extraction accuracy
- **Data Backup**: Create backup stages with independent field processing

---

*This guideline provides a standardized approach for creating pipeline duplication files that maintain data integrity while providing independent processing capabilities.*