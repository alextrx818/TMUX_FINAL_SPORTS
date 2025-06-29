#!/bin/bash

# Comprehensive Logging System Test Script
# Tests all 6 endpoints for active logging and folder structure

echo "🧪 TESTING LOGGING SYSTEM - ALL ENDPOINTS"
echo "=========================================="
echo "$(date '+%m/%d/%Y %I:%M:%S %p') EST"
echo ""

# Test results tracking
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to test endpoint logging
test_endpoint() {
    local endpoint_name="$1"
    local expected_file="logs/${endpoint_name}/${endpoint_name}.json"
    local archive_dir="logs/${endpoint_name}/archive"
    
    echo "📂 Testing ${endpoint_name^^} ENDPOINT:"
    echo "-----------------------------------"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    # Test 1: Check if log directory exists
    if [ -d "logs/${endpoint_name}" ]; then
        echo "✅ Directory exists: logs/${endpoint_name}/"
    else
        echo "❌ Directory missing: logs/${endpoint_name}/"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return
    fi
    
    # Test 2: Check if main log file exists
    if [ -f "$expected_file" ]; then
        echo "✅ Log file exists: ${expected_file}"
    else
        echo "❌ Log file missing: ${expected_file}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return
    fi
    
    # Test 3: Check if archive directory exists
    if [ -d "$archive_dir" ]; then
        echo "✅ Archive directory exists: ${archive_dir}/"
    else
        echo "⚠️  Archive directory missing: ${archive_dir}/ (will be created when needed)"
    fi
    
    # Test 4: Check log file size and content
    if [ -s "$expected_file" ]; then
        local file_size=$(stat -c%s "$expected_file" 2>/dev/null || echo "0")
        local line_count=$(wc -l < "$expected_file" 2>/dev/null || echo "0")
        echo "✅ Log file has content: ${file_size} bytes, ${line_count} lines"
        
        # Test 5: Check for recent entries (last 24 hours)
        local recent_entries=$(grep "$(date '+%Y-%m-%d')" "$expected_file" | wc -l 2>/dev/null || echo "0")
        if [ "$recent_entries" -gt 0 ]; then
            echo "✅ Recent entries found: ${recent_entries} from today"
        else
            # Check for entries from yesterday too
            local yesterday=$(date -d "yesterday" '+%Y-%m-%d')
            local yesterday_entries=$(grep "$yesterday" "$expected_file" | wc -l 2>/dev/null || echo "0")
            if [ "$yesterday_entries" -gt 0 ]; then
                echo "✅ Recent entries found: ${yesterday_entries} from yesterday"
            else
                echo "⚠️  No recent entries found (may be normal if just started)"
            fi
        fi
        
        # Test 6: Check JSON structure
        if python3 -m json.tool "$expected_file" > /dev/null 2>&1; then
            echo "✅ Valid JSON structure"
        else
            echo "❌ Invalid JSON structure"
            FAILED_TESTS=$((FAILED_TESTS + 1))
            return
        fi
        
        # Test 7: Check for required fields
        local has_timestamp=$(grep -c '"timestamp"' "$expected_file" 2>/dev/null || echo "0")
        local has_endpoint=$(grep -c '"endpoint".*'${endpoint_name}'"' "$expected_file" 2>/dev/null || echo "0")
        local has_status=$(grep -c '"status"' "$expected_file" 2>/dev/null || echo "0")
        
        if [ "$has_timestamp" -gt 0 ] && [ "$has_endpoint" -gt 0 ] && [ "$has_status" -gt 0 ]; then
            echo "✅ Required fields present (timestamp, endpoint, status)"
        else
            echo "❌ Missing required fields"
            FAILED_TESTS=$((FAILED_TESTS + 1))
            return
        fi
        
        # Test 8: Show latest entry timestamp
        local latest_timestamp=$(python3 -c "
import json
try:
    with open('$expected_file', 'r') as f:
        data = json.load(f)
    if data and len(data) > 0:
        print(data[0]['timestamp'][:19])
    else:
        print('No entries')
except:
    print('Error reading')
" 2>/dev/null || echo "Unable to read")
        echo "📅 Latest entry: ${latest_timestamp}"
        
    else
        echo "❌ Log file is empty: ${expected_file}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return
    fi
    
    PASSED_TESTS=$((PASSED_TESTS + 1))
    echo "✅ ${endpoint_name^^} ENDPOINT: ALL TESTS PASSED"
    echo ""
}

# Function to check overall system health
check_system_health() {
    echo "🏥 SYSTEM HEALTH CHECK:"
    echo "======================"
    
    # Check if pipeline is running
    if [ -f "pipeline.pid" ] && kill -0 $(cat pipeline.pid) 2>/dev/null; then
        local pid=$(cat pipeline.pid)
        echo "✅ Pipeline is running (PID: $pid)"
        
        # Check how long it's been running
        local start_time=$(ps -o lstart= -p $pid 2>/dev/null | xargs -I {} date -d "{}" +%s)
        local current_time=$(date +%s)
        local runtime=$((current_time - start_time))
        local runtime_formatted=$(printf '%02d:%02d:%02d' $((runtime/3600)) $((runtime%3600/60)) $((runtime%60)))
        echo "⏱️  Runtime: ${runtime_formatted}"
    else
        echo "❌ Pipeline is not running"
    fi
    
    # Check logs directory structure
    echo ""
    echo "📁 Directory Structure:"
    if [ -d "logs" ]; then
        echo "✅ Main logs directory exists"
        local endpoint_count=$(find logs -maxdepth 1 -type d | grep -v "^logs$" | wc -l)
        echo "📊 Endpoint directories: ${endpoint_count}/6"
        
        # List all endpoint directories
        for dir in logs/*/; do
            if [ -d "$dir" ]; then
                local endpoint=$(basename "$dir")
                local file_count=$(find "$dir" -name "*.json" | wc -l)
                echo "   📂 ${endpoint}: ${file_count} JSON files"
            fi
        done
    else
        echo "❌ Main logs directory missing"
    fi
    
    echo ""
}

# Function to show statistics
show_statistics() {
    echo "📊 LOGGING STATISTICS:"
    echo "====================="
    
    for endpoint in live details odds teams competitions countries; do
        local log_file="logs/${endpoint}/${endpoint}.json"
        if [ -f "$log_file" ]; then
            local total_entries=$(python3 -c "
import json
try:
    with open('$log_file', 'r') as f:
        data = json.load(f)
    print(len(data))
except:
    print(0)
" 2>/dev/null || echo "0")
            
            local success_count=$(grep -c '"status": "success"' "$log_file" 2>/dev/null || echo "0")
            local failed_count=$(grep -c '"status": "failed"' "$log_file" 2>/dev/null || echo "0")
            
            if [ "$total_entries" -gt 0 ]; then
                local success_rate=$(python3 -c "print(f'{($success_count/$total_entries)*100:.1f}')" 2>/dev/null || echo "0.0")
                echo "📈 ${endpoint^^}: ${total_entries} entries, ${success_count} success, ${failed_count} failed (${success_rate}% success rate)"
            else
                echo "📈 ${endpoint^^}: No entries"
            fi
        else
            echo "📈 ${endpoint^^}: No log file"
        fi
    done
    echo ""
}

# Main execution
echo "Starting comprehensive test of all 6 endpoints..."
echo ""

# Check system health first
check_system_health

# Test each endpoint
for endpoint in live details odds teams competitions countries; do
    test_endpoint "$endpoint"
done

# Show statistics
show_statistics

# Final summary
echo "🎯 FINAL TEST RESULTS:"
echo "====================="
echo "Total Tests: ${TOTAL_TESTS}"
echo "Passed: ${PASSED_TESTS}"
echo "Failed: ${FAILED_TESTS}"

if [ $FAILED_TESTS -eq 0 ]; then
    echo "🎉 ALL TESTS PASSED - LOGGING SYSTEM FULLY OPERATIONAL!"
    exit 0
else
    echo "⚠️  ${FAILED_TESTS} TESTS FAILED - ISSUES DETECTED"
    exit 1
fi