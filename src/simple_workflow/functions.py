
"""
Simple workflow handlers for AGNT5.

This module demonstrates basic workflow operations using AGNT5 function handlers.
"""

import logging
from agnt5.decorators import function
from agnt5.workflows import (
    FlowDefinition,
    task_step,
    wait_signal_step,
    wait_timer_step,
    workflow,
)

logger = logging.getLogger(__name__)


@function(name="process_task")
def process_task(ctx, task_id: str, task_data: dict) -> dict:
    """
    Process a workflow task.
    
    Args:
        ctx: Execution context (provided by AGNT5)
        task_id: Unique identifier for the task
        task_data: Task payload data
        
    Returns:
        Dict with processed task results
    """
    logger.info(f"Processing task {task_id} with data: {task_data}")
    
    # Simulate some processing
    processed_data = {
        "task_id": task_id,
        "original_data": task_data,
        "status": "completed",
        "processed_at": str(ctx) if ctx else "unknown_context",
        "message": f"Successfully processed task {task_id}"
    }
    
    logger.info(f"Task {task_id} processed successfully")
    return processed_data


@function(name="validate_input")
def validate_input(ctx, input_data: dict, rules: list = None) -> dict:
    """
    Validate input data against specified rules.
    
    Args:
        ctx: Execution context (provided by AGNT5)
        input_data: Data to validate
        rules: List of validation rules (optional)
        
    Returns:
        Dict with validation results
    """
    logger.info(f"Validating input: {input_data}")
    
    # Default rules if none provided
    if rules is None:
        rules = ["required_fields", "data_types"]
    
    # Simple validation logic
    errors = []
    warnings = []
    
    # Check if required fields exist (example rule)
    if "required_fields" in rules:
        required = ["id", "type"]
        for field in required:
            if field not in input_data:
                errors.append(f"Missing required field: {field}")
    
    # Check data types (example rule)
    if "data_types" in rules:
        if "id" in input_data and not isinstance(input_data["id"], str):
            errors.append("Field 'id' must be a string")
        if "value" in input_data and not isinstance(input_data["value"], (int, float)):
            warnings.append("Field 'value' should be numeric")
    
    is_valid = len(errors) == 0
    
    result = {
        "valid": is_valid,
        "errors": errors,
        "warnings": warnings,
        "input_data": input_data,
        "rules_applied": rules
    }
    
    logger.info(f"Validation result: {'valid' if is_valid else 'invalid'}")
    return result


@function(name="calculate_metrics")
def calculate_metrics(ctx, data_points: list, metric_type: str = "average") -> dict:
    """
    Calculate metrics from a list of data points.
    
    Args:
        ctx: Execution context (provided by AGNT5)
        data_points: List of numeric values
        metric_type: Type of metric to calculate (average, sum, min, max)
        
    Returns:
        Dict with calculated metrics
    """
    logger.info(f"Calculating {metric_type} for {len(data_points)} data points")
    
    if not data_points:
        return {
            "metric_type": metric_type,
            "result": None,
            "error": "No data points provided"
        }
    
    try:
        # Convert to numbers
        numbers = [float(x) for x in data_points]
        
        # Calculate based on type
        if metric_type == "average":
            result = sum(numbers) / len(numbers)
        elif metric_type == "sum":
            result = sum(numbers)
        elif metric_type == "min":
            result = min(numbers)
        elif metric_type == "max":
            result = max(numbers)
        else:
            return {
                "metric_type": metric_type,
                "result": None,
                "error": f"Unknown metric type: {metric_type}"
            }
        
        logger.info(f"Calculated {metric_type}: {result}")
        return {
            "metric_type": metric_type,
            "result": result,
            "data_points_count": len(numbers),
            "input_data": data_points
        }
        
    except (ValueError, TypeError) as e:
        logger.error(f"Error calculating metrics: {e}")
        return {
            "metric_type": metric_type,
            "result": None,
            "error": f"Invalid data: {str(e)}"
        }


@function(name="health_check")
def health_check(ctx) -> dict:
    """
    Simple health check function.
    
    Args:
        ctx: Execution context (provided by AGNT5)
        
    Returns:
        Dict with health status
    """
    return {
        "status": "healthy",
        "service": "simple-workflow",
        "timestamp": str(ctx) if ctx else "unknown_context",
        "message": "Service is running normally"
    }


@workflow("simple_sequence")
def build_simple_sequence_flow() -> FlowDefinition:
    """Register a simple two-step workflow definition."""

    return FlowDefinition(
        steps=[
            task_step(
                name="validate",
                service_name="simple-workflow",
                handler_name="validate_input",
                input_data={
                    "input_data": {"id": "{{id}}", "type": "{{type}}"},
                },
            ),
            task_step(
                name="process",
                service_name="simple-workflow",
                handler_name="process_task",
                dependencies=["validate"],
                input_data={
                    "task_id": "{{task_id}}",
                    "task_data": {"source": "workflow"},
                },
            ),
        ],
    )


@workflow("metrics_with_signal")
def build_metrics_signal_flow() -> FlowDefinition:
    """Register a workflow that waits on an external signal before calculating metrics."""

    return FlowDefinition(
        steps=[
            wait_signal_step(
                name="await_ready",
                signal_name="metrics_ready",
            ),
            task_step(
                name="calculate",
                service_name="simple-workflow",
                handler_name="calculate_metrics",
                dependencies=["await_ready"],
                input_data={
                    "data_points": [1, 2, 3, 4, 5],
                    "metric_type": "average",
                },
            ),
            wait_timer_step(
                name="cooldown",
                timer_key="metrics_cooldown",
                dependencies=["calculate"],
                delay_ms=2_000,
            ),
        ],
    )
