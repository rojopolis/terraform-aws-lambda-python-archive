variable "src_dir" {
  description = "Path to root of Python source to package."
  type        = "string"
}

variable "output_path" {
  description = "The output of the archive file."
  type        = "string"
}

variable "install_dependencies" {
  description = "Whether to install pip dependecies"
  type        = bool
  default     = true
}
