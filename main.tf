data "external" "lambda_archive" {
    program = ["python", "${path.module}/scripts/build_lambda.py"]
    query = {
        src_dir     = "${var.src_dir}"
        output_path = "${var.output_path}"
    }
}