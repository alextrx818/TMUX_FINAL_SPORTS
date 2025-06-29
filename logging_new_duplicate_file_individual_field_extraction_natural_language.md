# AI Helper Instructions: Building Safe Data Processing Steps (Natural Language Version)

## Quick Summary

This guide helps AI assistants create new data processing steps that safely handle sports match data. Think of it like following a recipe to carefully transform sports information without breaking anything.

## Step-by-Step Process

### 1. Understand Your Task
- Find out what data file you're reading from (usually monitoring.json)
- Decide what your new processing step will do with that data
- Choose a name for your new file (like alert.py, analysis.py, filtering.py)

### 2. Build the Foundation First (Skeleton Phase)
**IMPORTANT**: Create the basic structure before doing any actual data processing!

1. **Set up the empty functions** - Create functions that will eventually do the work, but leave them mostly empty for now
2. **Add safety patterns** - Make sure every piece of code can handle problems gracefully (like missing data or broken files)
3. **Test the skeleton** - Make sure your empty structure works before adding real processing
4. **Connect to the pipeline** - Ensure your new step gets called automatically by the previous step

### 3. Add the Real Processing (Implementation Phase)
**Only do this after Step 2 is complete!**

1. **Extract each field individually** - Don't copy entire chunks of data; process each piece separately
2. **Apply safety checks** - For every field you extract, check if it exists and is the right type before using it
3. **Keep the same structure** - Your output should have the same organization as the input, just with your processing applied
4. **Handle errors gracefully** - If something goes wrong with one field, don't crash the whole process

### 4. Required Safety Patterns

#### Safe Data Access
- Always check if a field exists before trying to use it
- Provide backup default values if data is missing
- Never assume data will be in the expected format

#### Type Checking
- Before processing any data, verify it's the type you expect (text, number, list, etc.)
- If it's not the right type, handle it safely instead of crashing

#### Array/List Safety
- Before accessing items in a list, check that the list has enough items
- Don't assume lists will always have the data you expect

#### Error Handling
- Wrap risky operations in try/catch blocks
- If something fails, log the problem and continue with a safe default

### 5. File Organization
- **Your new file**: Goes in the main project folder (like `/workspaces/TMUX_FINAL_SPORTS/your_file.py`)
- **Input data**: Usually comes from `/workspaces/TMUX_FINAL_SPORTS/logs/monitoring/monitoring.json`
- **Output data**: Goes to `/workspaces/TMUX_FINAL_SPORTS/logs/your_stage_name/your_stage_name.json`

### 6. Automatic Pipeline Integration
When your processing step finishes successfully, it should automatically call the next step in the pipeline. This happens by adding code that runs the next Python file when your step completes.

**Example**: If you create `alert.py`, you'd add code to the previous stage (monitoring.py) to automatically run `alert.py` when monitoring.py finishes.

### 7. Individual Field Processing
**Critical Rule**: Process each piece of data separately, don't take shortcuts.

Instead of copying entire sections of data, extract each field one by one:
- Get the match ID separately
- Get the team names separately  
- Get the scores separately
- Get the competition name separately
- And so on...

This ensures you understand and control every piece of data that flows through your system.

### 8. Structure Preservation
Your output should look very similar to your input, just with your processing applied. If the input has teams organized under a "teams" section with "home" and "away" subsections, your output should maintain that same organization.

### 9. Quality Standards
- **Safety First**: Your code should handle problems gracefully without crashing
- **Individual Processing**: Every field should be extracted and processed separately
- **Structure Maintained**: The organization of data should remain consistent
- **Error Resilience**: Missing or corrupted data shouldn't break the entire process

### 10. What NOT to Do
- Don't copy entire chunks of data without processing each field
- Don't access data directly without checking if it exists first
- Don't assume arrays/lists will have items without checking the length
- Don't skip type validation
- Don't add actual processing logic during the skeleton phase

### 11. Success Criteria

#### Phase 1 Complete (Skeleton):
- All required functions created with proper structure
- Safety patterns applied to all data access
- Input and output file paths configured correctly
- Error handling implemented
- No actual processing logic yet - just the framework

#### Phase 2 Complete (Implementation):
- Every field from the input file individually extracted and processed
- Identical data organization preserved in output
- All safety patterns consistently applied
- Independent processing logic for each field
- Proper file output with timestamps and metadata

## Pipeline Position
Your new stage fits into the continuous data processing pipeline:
`monitoring.py → YOUR NEW STAGE → future stages`

The system runs automatically every minute, processing live sports data through each stage in sequence.

## Remember
1. **Skeleton first** - Build the structure before adding processing logic
2. **Individual extraction** - Process each field separately, no shortcuts
3. **Safety always** - Apply protective patterns consistently
4. **Structure preservation** - Keep the same data organization
5. **Pipeline integration** - Connect to the automatic calling system

This approach creates reliable, maintainable data processing steps that handle sports information safely and consistently.