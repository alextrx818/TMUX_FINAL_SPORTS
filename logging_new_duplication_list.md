# Universal Data Pipeline Logging Architecture - Perfect Standard FINAL

## PERFECT STANDARD IMPLEMENTATION GUIDE
**Based on the successful monitoring.py implementation - June 29, 2025**

### **What This Creates**
When you follow this guide, you'll create three things immediately:
1. A new Python file that processes data with field-by-field extraction
2. A matching JSON log file that stores results with accumulating log pattern
3. An archive folder that keeps old data organized with 50-fetch rotation

### **Universal Data Pipeline Logging Architecture**
Every new file you create will read data from the previous file, systematically extract every single field, and save it to its own accumulating log file. This creates a sequential processing chain where each stage processes the latest fetch from the previous stage.

### **Pipeline Flow Pattern**
The entire system runs automatically every 60 seconds. Each time it runs, fresh data gets fetched from the API and flows through every file in the pipeline. Your new file will read from the previous stage's accumulating log and process the most recent fetch data.

### **Field-by-Field Processing Standard**
Every field must be individually identified and extracted. Never bulk copy or mirror data. Each field gets its own extraction logic, even if it's simple pass-through. This ensures complete data processing coverage and maintains the Universal Data Pipeline Logging Architecture.

### **Accumulating Log Pattern**
All files use the accumulating log pattern with 50-fetch rotation. This means each file maintains a history of its last 50 processing runs, with older data automatically archived. This creates a rolling window of recent processing activity while preserving historical data.

## Perfect Standard Implementation Process
**Based on the successful monitoring.py implementation that the user praised as "THE PERFECT NEW FILE ADDED TO PIPELIEN CREATION FORMAT STANDARD"**

### **Step 1: Plan Your File**
- Decide what you want to name your new file
- Figure out which existing file should call your new file
- Know exactly which JSON file your new file will read from
- Remember that if you create "alert.py", it will create "alert.json"

### **Step 2: Create the File Structure**
- Make a new Python file with your chosen name
- **IMMEDIATELY CREATE** the matching JSON log file in the right folder with initial accumulating structure
- **IMMEDIATELY CREATE** the archive folder for old data
- Don't wait for the code to create them - create them manually as part of setup

### **Step 3: Implement Source Data Reading (MANDATORY)**

**CRITICAL REQUIREMENT**: Read from Previous Stage's Accumulating Log

```python
def load_previous_stage_data() -> Optional[Dict[str, Any]]:
    """Load previous stage data with error handling"""
    source_file = '/workspaces/TMUX_FINAL_SPORTS/logs/previous_stage/previous_stage.json'
    
    try:
        if os.path.exists(source_file):
            with open(source_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print(f"ERROR: Source file not found: {source_file}")
            return None
    except Exception as e:
        print(f"ERROR: Failed to load data: {e}")
        return None

def extract_latest_matches(source_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract matches from accumulating log structure"""
    if "fetch_history" in source_data and source_data["fetch_history"]:
        # Get latest fetch from accumulating log
        latest_fetch = source_data["fetch_history"][-1]
        return latest_fetch.get("processed_data", {}).get("matches", [])
    else:
        # Fallback for non-accumulating log sources
        return source_data.get("matches", [])
```

### **Step 4: Implement Field-by-Field Processing (MANDATORY)**

**CRITICAL REQUIREMENT**: Every field must be individually identified and extracted. Never bulk copy or mirror data.

**Field Processing Standards**:
- Create an `extract_match_fields()` function that processes every single field
- Each field gets its own extraction logic, even if it's simple pass-through
- Use systematic field processing: loop through each field in the source data
- Include field validation and type conversion where appropriate
- Handle nested structures (competition, teams, odds, environment) with proper extraction
- Add field conversion logic if needed (like array-to-individual-fields conversion)
- Default behavior: simple pass-through with proper validation

**Example Implementation Pattern**:
```python
def extract_match_fields(match: Dict[str, Any]) -> Dict[str, Any]:
    extracted = {}
    
    # SYSTEMATIC FIELD PROCESSING: Process every field from source
    for field_name, field_value in match.items():
        # FIELD IDENTIFICATION (MANDATORY) + OPTIONAL TASK ASSIGNMENT
        extracted[field_name] = field_value  # Default: Simple pass-through
        
        # OPTIONAL TASKS: Add specific processing if needed
        # if field_name == "home_scores" and isinstance(field_value, list):
        #     # Convert array to individual fields
        #     extracted["home_score_current"] = field_value[0]
        #     extracted["home_score_half"] = field_value[1]
    
    return extracted
```

### **Step 5: Implement Universal Data Pipeline Logging Architecture (MANDATORY)**

**CRITICAL REQUIREMENTS**:

**A. Load Existing Log Function**:
```python
def load_existing_log() -> Dict[str, Any]:
    log_file = '/workspaces/TMUX_FINAL_SPORTS/logs/{filename}/{filename}.json'
    
    try:
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {
                "log_metadata": {
                    "total_fetches": 0,
                    "first_fetch": "",
                    "last_fetch": "",
                    "log_format": "accumulating_v1.0"
                },
                "fetch_history": []
            }
    except Exception as e:
        # Return new structure on error
```

**B. Archive Function with 50-Fetch Rotation**:
```python
def archive_old_fetches(accumulated_log: Dict[str, Any]) -> Dict[str, Any]:
    max_history = 50
    
    if len(accumulated_log["fetch_history"]) > max_history:
        # Create archive directory
        archive_dir = '/workspaces/TMUX_FINAL_SPORTS/logs/{filename}/archive'
        os.makedirs(archive_dir, exist_ok=True)
        
        # Archive excess fetches with NY timezone timestamp
        excess_fetches = accumulated_log["fetch_history"][:-max_history]
        ny_tz = pytz.timezone('US/Eastern')
        archive_timestamp = datetime.now(ny_tz).strftime('%Y%m%d_%H%M%S')
        archive_file = f"{archive_dir}/{filename}_archive_{archive_timestamp}.json"
        
        # Keep only last 50 fetches
        accumulated_log["fetch_history"] = accumulated_log["fetch_history"][-max_history:]
    
    return accumulated_log
```

**C. Save Function with Accumulating Pattern**:
```python
def save_data(processed_matches: List[Dict[str, Any]]) -> bool:
    # Load existing accumulating log
    accumulated_log = load_existing_log()
    
    # Get NY timezone
    ny_tz = pytz.timezone('US/Eastern')
    current_time = datetime.now(ny_tz)
    
    # Create new fetch entry
    new_fetch_entry = {
        "fetch_timestamp": current_time.isoformat(),
        "fetch_number": len(accumulated_log["fetch_history"]) + 1,
        "processed_data": {
            "matches": processed_matches,
            "total_matches": len(processed_matches)
        },
        "processing_metadata": {
            "source_file": "previous_stage.json",
            "processing_time": current_time.strftime('%m/%d/%Y %I:%M:%S %p %Z'),
            "status": "success"
        }
    }
    
    # Add new fetch to history
    accumulated_log["fetch_history"].append(new_fetch_entry)
    
    # Update metadata
    accumulated_log["log_metadata"]["total_fetches"] = len(accumulated_log["fetch_history"])
    accumulated_log["log_metadata"]["last_fetch"] = current_time.isoformat()
    if accumulated_log["log_metadata"]["total_fetches"] == 1:
        accumulated_log["log_metadata"]["first_fetch"] = current_time.isoformat()
    
    # Archive old fetches if exceeding 50
    accumulated_log = archive_old_fetches(accumulated_log)
    
    # Save accumulating log
    # MANDATORY: NY Eastern time footer (LAST LINE OF EVERY FETCH)
    ny_time_footer = current_time.strftime('%m/%d/%Y %I:%M:%S %p')
    print(f"✅ {filename}.py completed: {ny_time_footer} EST")
    
    return True
```

### **Step 6: Save Everything Properly**
- Save your processed data to your file's own JSON log
- Include metadata like processing time and number of items processed
- Use New York Eastern time for all timestamps
- Print a completion message with New York Eastern time as the very last thing
- Make sure the archive system works automatically every 50 fetches
- Every API fetch that happens every 60 seconds must have a New York timestamp

### **Step 7: Implement Pipeline Integration (MANDATORY)**

**A. Add trigger_next_stage() Function to Your File** (if not terminal):
```python
def trigger_next_stage():
    """Call next_stage.py"""
    print(f"\n🔄 Calling next_stage.py for processing...")
    
    try:
        subprocess.run(['python3', 'next_stage.py'], check=True)
        print(f"✅ next_stage.py completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running next_stage.py: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error with next_stage.py: {e}")
        return 1
    
    return 0
```

**B. Update Previous File to Call Your New File**:
```python
def trigger_next_stage():
    """Call your_new_file.py stage"""
    print(f"\n🔄 Calling your_new_file.py for processing...")
    
    try:
        subprocess.run(['python3', 'your_new_file.py'], check=True)
        print(f"✅ your_new_file.py completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running your_new_file.py: {e}")
        return 1
    
    return 0
```

**C. Add to Previous File's Main Function**:
```python
if success:
    # Call next stage in pipeline
    exit_code = trigger_next_stage()
    return exit_code
```

### **Manual Setup Required (DO NOT SKIP)**

**IMMEDIATE SETUP TASKS - MUST BE DONE FIRST**:

1. **CREATE** the main directory:
   ```bash
   mkdir -p /workspaces/TMUX_FINAL_SPORTS/logs/{filename}/
   ```

2. **CREATE** the archive directory:
   ```bash
   mkdir -p /workspaces/TMUX_FINAL_SPORTS/logs/{filename}/archive/
   ```

3. **CREATE** the initial JSON file: `/workspaces/TMUX_FINAL_SPORTS/logs/{filename}/{filename}.json`
   ```json
   {
     "log_metadata": {
       "total_fetches": 0,
       "first_fetch": "",
       "last_fetch": "",
       "log_format": "accumulating_v1.0"
     },
     "fetch_history": []
   }
   ```

4. **VERIFY** permissions and file structure before testing

**CRITICAL**: These directories and initial files MUST exist before running your new Python file for the first time. The Universal Data Pipeline Logging Architecture requires this exact structure.

### **What Happens After Creation - Universal Data Pipeline Logging Architecture**
- Your file becomes part of the sequential processing chain
- Every 60 seconds when fresh data comes in, your file processes the latest fetch from the previous stage
- Your file reads from the previous stage's accumulating log and extracts the most recent fetch data
- Your file performs systematic field-by-field processing on every piece of data
- Your file maintains its own accumulating log with rolling 50-fetch history
- Old data automatically gets archived with proper NY Eastern timestamps
- Your file becomes a permanent part of the Universal Data Pipeline Logging Architecture
- Each processing run creates a new fetch entry with complete metadata and processing information

### **Key Points to Remember - Perfect Standard Implementation**

**Pipeline Behavior**:
- The pipeline runs every 60 seconds automatically
- Your file processes the latest fetch from the previous stage's accumulating log
- Your file performs mandatory field-by-field processing (never bulk copy)
- Every field gets individual identification and extraction logic
- Default behavior is validated pass-through with proper type handling

**Universal Data Pipeline Logging Architecture**:
- All files use the identical accumulating log pattern with 50-fetch rotation
- Every fetch gets timestamped with New York Eastern time in ISO format
- Archive rotation happens automatically when exceeding 50 fetches
- Each file maintains complete fetch history with processing metadata
- Pipeline flow: previous_stage.json → your_file.py → your_file.json → next_stage.py

**Field Processing Standards**:
- Systematic field processing with individual field extraction
- Proper handling of nested structures (competition, teams, odds, environment)
- Field validation and type conversion where appropriate
- Optional field conversion logic (like array-to-individual-fields)
- Complete data processing coverage with no field left unprocessed

**Integration Requirements**:
- Must implement load_previous_stage_data() function
- Must implement extract_match_fields() function with systematic processing
- Must implement accumulating log pattern with archive rotation
- Must include trigger_next_stage() function (if not terminal)
- Must use NY Eastern timezone for all timestamps
- Must print completion message with NY Eastern time as final output

---

## PERFECT STANDARD SUMMARY - THE MONITORING.PY MODEL

**This documentation represents the complete Perfect Standard Implementation Guide based on the successful monitoring.py implementation that was praised by the user as "THE PERFECT NEW FILE ADDED TO PIPELIEN CREATION FORMAT STANDARD."**

### **Core Architecture Components**:
1. **Universal Data Pipeline Logging Architecture** with accumulating log pattern
2. **Field-by-Field Processing Standard** with systematic extraction
3. **50-Fetch Rotation System** with automatic archiving
4. **Sequential Pipeline Integration** with proper stage calling
5. **NY Eastern Timezone Standardization** for all operations

### **Success Criteria**:
- ✅ Reads from previous stage's accumulating log (latest fetch)
- ✅ Performs systematic field-by-field processing
- ✅ Maintains own accumulating log with 50-fetch rotation
- ✅ Archives old data automatically with proper timestamps
- ✅ Calls next stage in pipeline (if not terminal)
- ✅ Uses NY Eastern timezone for all timestamps
- ✅ Prints completion message as final output

### **Implementation Result**:
When implemented correctly, this standard produces files that:
- Integrate seamlessly into the 60-second data pipeline
- Process every field individually with complete coverage
- Maintain rolling history with automatic archiving
- Preserve all data while managing storage efficiently
- Follow identical patterns for consistency across all stages

**This is the definitive standard for creating new files in the Universal Data Pipeline Logging Architecture.**

---

## PIPELINE WORKFLOW PERMISSION RULE

**Effective: June 29, 2025**

### **New File Creation Permission Protocol**

When a new file is created, it almost always means that the last file in the pipeline is completed. The following permission rule applies to maintain pipeline integrity:

**PERMISSION REQUIREMENT**: Any future edits or adjustments other than the calling logic that is already included (including any other logic that requires editing for initial file creation) can be applied according to this documentation. However, any other edits after that while working on the next file should request permission first.

**RATIONALE**: If we are working on the next file, it means we are mostly likely done with the last file. Additional modifications to completed pipeline stages should be coordinated to avoid conflicts and maintain system stability.

**WORKFLOW**: 
1. Complete current pipeline stage implementation
2. Verify calling logic and integration
3. Move to next pipeline stage
4. Request permission for any additional modifications to previous stages

This rule ensures pipeline stability while allowing necessary adjustments for initial file creation and integration.