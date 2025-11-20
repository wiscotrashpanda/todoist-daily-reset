resource "aws_cloudwatch_event_rule" "nightly_schedule" {
  name                = "todoist-nightly-rollover"
  description         = "Triggers Todoist rollover lambda at 06:00 UTC (Midnight CST)"
  schedule_expression = "cron(0 6 * * ? *)"
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.nightly_schedule.name
  target_id = "SendToLambda"
  arn       = aws_lambda_function.rollover_func.arn
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.rollover_func.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.nightly_schedule.arn
}
