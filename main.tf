data "external" "lambda_archive" {
  program = ["python3", "${path.module}/scripts/build_lambda.py"]
  query = {
    src_dir     = "${var.src_dir}"
    output_path = "${var.output_path}"
  }
}
