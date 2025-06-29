# Universal Data Pipeline Logging Architecture

## Sequential Data Flow Principle
Each file in the pipeline reads from exactly **one specific previous file** and outputs to its **own dedicated file**. This creates a linear transformation chain where data flows sequentially through specialized processing stages.

## File Processing Pattern
```
Input Source → [Optional: Process/Transform] → Output Destination → Trigger Next Stage
```

**Standard Implementation:**
- **Read**: Load data from single designated source file
- **Process**: *(Optional)* Apply specific transformations (filter, convert, extract, analyze)  
- **Output**: Save results to own dedicated log file with metadata
- **Trigger**: Call next stage via subprocess (if not terminal)

**Note**: Processing/transformation is completely optional. A file can simply load data from the previous stage and log it with updated metadata and timestamps without any data modification.

## Independence & Reliability Principles

### 1. Single Source Dependency
- Each file reads from **one and only one** previous file
- No cross-dependencies or complex data relationships
- Clear, predictable data lineage

### 2. Isolated Error Handling
- Each file has independent error recovery mechanisms
- Failures in one stage don't cascade to other stages  
- Graceful degradation with fallback behaviors

### 3. Self-Contained Logging
- Each file manages its own logging completely independently
- Hardcoded file paths specific to that stage
- No shared logging utilities or centralized dependencies

### 4. Metadata Preservation
- Each stage includes processing metadata (timestamps, counts, versions)
- NYC Eastern timezone standardization across all stages
- Performance tracking and completion verification

### 5. Directory Auto-Management
- Files create their own output directories if needed
- No shared infrastructure dependencies
- Consistent UTF-8 encoding and JSON formatting

### 6. Naming Convention for Log Files
- **Log file name matches Python file name**: If you create `alert.py`, the log will be `alert.json` (or `alert.md`, `alert.logging` as specified)
- **Default log format**: JSON (unless otherwise specified)
- **Log directory structure**: `/workspaces/TMUX_FINAL_SPORTS/logs/{filename}/{filename}.{extension}`
- **Examples**:
  - `alert.py` → `/workspaces/TMUX_FINAL_SPORTS/logs/alert/alert.json`
  - `backup.py` → `/workspaces/TMUX_FINAL_SPORTS/logs/backup/backup.json`
  - `validation.py` → `/workspaces/TMUX_FINAL_SPORTS/logs/validation/validation.json`

### 7. Accumulating Log Pattern (MANDATORY)
**CRITICAL REQUIREMENT**: All pipeline files must use **accumulating log structure** with fetch history preservation and automatic rotation.

**Standard Accumulating Structure**:
```json
{
  "log_metadata": {
    "total_fetches": 0,
    "first_fetch": "ISO timestamp",
    "last_fetch": "ISO timestamp", 
    "log_format": "accumulating_v1.0"
  },
  "fetch_history": [
    {
      "fetch_timestamp": "ISO timestamp",
      "fetch_number": 1,
      "processed_data": { /* your field-by-field extracted data */ },
      "processing_metadata": { /* timestamps, counts, etc. */ }
    }
  ]
}
```

**Implementation Requirements**:
1. ✅ **Load existing log file** if it exists (don't overwrite)
2. ✅ **Add new fetch entry** to `fetch_history[]` array
3. ✅ **Update metadata counters** (`total_fetches`, `last_fetch`)
4. ✅ **Implement 100-fetch rotation** - keep only last 100 entries
5. ✅ **Save complete accumulating structure** (mode 'w' only after building full structure)

**Rotation Logic** (when `fetch_history` exceeds 100 entries):
```python
max_history = 100
if len(accumulated_log["fetch_history"]) > max_history:
    accumulated_log["fetch_history"] = accumulated_log["fetch_history"][-max_history:]
    accumulated_log["log_metadata"]["total_fetches"] = max_history
    accumulated_log["log_metadata"]["first_fetch"] = accumulated_log["fetch_history"][0]["fetch_timestamp"]
```

**Anti-Pattern (PROHIBITED)**:
- ❌ **Single-file overwrite logging** (mode 'w' without loading existing)
- ❌ **Losing fetch history** between executions
- ❌ **No rotation logic** (allowing unlimited file growth)
- ❌ **Inconsistent log structure** across pipeline files

## Application to New Files

When creating any new file in this architecture:

1. **Identify single input source** - determine which existing file provides your data
2. **Define transformation purpose** *(Optional)* - what specific processing will this stage perform, or simply pass-through with updated logging
3. **Create dedicated output path** - establish where this stage will save its results
4. **Implement independent error handling** - no dependencies on other files' error systems
5. **Add pipeline trigger** - call next stage via subprocess (unless terminal)
6. **Include processing metadata** - timestamps, counts, source references, completion status

### Field-by-Field Processing Implementation
**CRITICAL REQUIREMENT**: Each new file must **identify, extract, and analyze every single field** from the previous file. This ensures complete data integrity and traceability.

**Implementation Pattern**:
1. **Load source data** from previous stage
2. **Iterate through every field** in the source JSON structure
3. **For each field identified**:
   - **If task assigned**: Apply specific processing (convert, filter, parse, transform)
   - **If no task**: Pure pass-through with field preservation
4. **Independent field extraction** - no lazy copying, mirroring, or bulk operations
5. **Rebuild complete structure** with all fields accounted for
6. **Add processing metadata** and save to own log file

**Field Processing Examples**:
- `temperature: "19°C"` → **Task**: Convert to Fahrenheit → `temperature: "66°F"`
- `match_id: "abc123"` → **No Task**: Pass-through → `match_id: "abc123"`
- `odds[2][4]: 0.85` → **Task**: Convert to American odds → `odds[2][4]: "-117"`
- `team.name: "Arsenal"` → **No Task**: Pass-through → `team.name: "Arsenal"`

**Anti-Pattern (Prohibited)**:
- ❌ Bulk copying entire objects without field identification
- ❌ Lazy mirroring of data structures
- ❌ Skipping field analysis for "convenience"
- ❌ Assuming field contents without explicit extraction

This ensures every field is consciously processed and tracked through the pipeline.

This pattern ensures that adding new processing stages never breaks existing functionality and maintains the system's reliability through complete stage independence.