module "python_lambda_archive" {
    # Original version:
    # source = "rojopolis/lambda-python-archive/aws"
    # Updates past v0.1.6:
    source = "github.com/farfromunique/terraform-aws-lambda-python-archive.git?ref=0.1.8"

    src_dir              = "${path.module}/python"
    output_path          = "${path.module}/lambda.zip"
    install_dependencies = false
    # Requires v0.1.8 or more.
    exclude_files        = [
        '.gitignore',
        # Any other file(s) you don't want included
        # I use pipenv for local development, but prefer requirements.txt for deployments
        'Pipfile',
        'Pipfile.lock',
        '.env'
    ]
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
