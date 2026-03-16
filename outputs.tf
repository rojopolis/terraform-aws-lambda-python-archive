output "archive_path" {
  description = "Path of the archive file."
  value       = "${data.external.lambda_archive.result.archive}"
}

output "source_code_hash" {
  description = "Base64 encoded SHA256 hash of the archive file."
  value       = "${data.external.lambda_archive.result.base64sha256}"
}
