module "python_lambda_archive" {
    source      = "../"
    src_dir     = "${path.module}/python"
    output_path = "${path.module}/artifacts/lambda.zip"
}

resource "aws_iam_role" "iam_for_lambda" {
  name = "iam_for_lambda"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_lambda_function" "test_lambda" {
  filename         = "${module.python_lambda_archive.archive_path}"
  function_name    = "lambda_function_name"
  role             = "${aws_iam_role.iam_for_lambda.arn}"
  handler          = "exports.test"
  source_code_hash = "${module.python_lambda_archive.source_code_hash}"
  runtime          = "python3.6"

  environment {
    variables = {
      foo = "bar"
    }
  }
}
