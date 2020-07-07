# terraform-aws-lamba-python-archive
Package python source and dependencies into Lambda package with stable hash.

See: https://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html

I created this module because using the standard technique of using an
 `archive_file` data source has a few shortcomings:
1. This doesn't allow processing a requirements file.
2. Each apply results in a diff in `source_code_hash` becuase the archive includes
metadata and generated files (*.pyc).  This module doesn't include file metadata
or .pyc files in the archive so the hash is stable unless the source or dependencies
change. 

## Example

```
module "python_lambda_archive" {
    source = "rojopolis/lambda-python-archive/aws"

    src_dir              = "${path.module}/python"
    output_path          = "${path.module}/lambda.zip"
    install_dependencies = false
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
```

## External Dependencies
1. Python3.4+