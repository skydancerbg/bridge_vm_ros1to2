# Full Map Restored After Cropping

## Decision

Use the full static map export rather than the earlier cropped-map experiment.

## Reason

The project tried cropping against the real ROS occupancy grid, then rolled it back to restore full-map behavior. The frontend should consume metadata dynamically rather than assume cropped dimensions.

## Current Map

Current cached dimensions:
- Width: `4992`
- Height: `4992`
- Resolution: `0.019999999552965164`
- Origin: `(-50.0, -50.0, 0.0)`

## Guardrail

Do not hard-code old cropped extents in the frontend.

