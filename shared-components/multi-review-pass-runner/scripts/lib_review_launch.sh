#!/usr/bin/env bash
# Shared reviewer CLI launch helpers.

select_prompt_flag() {
  local cli="$1"
  local help_text
  help_text="$("$cli" --help 2>&1 || true)"

  if printf '%s\n' "$help_text" | grep -Eq -- '(^|[[:space:],])-p([,[:space:]]|$)'; then
    printf '%s\n' "-p"
  elif printf '%s\n' "$help_text" | grep -Eq -- '(^|[[:space:]])--print([,[:space:]]|$)'; then
    printf '%s\n' "--print"
  else
    printf '%s\n' "-p"
  fi
}

alternate_prompt_flag() {
  if [ "$1" = "-p" ]; then
    printf '%s\n' "--print"
  else
    printf '%s\n' "-p"
  fi
}

is_prompt_flag_usage_error() {
  local stderr_file="$1"

  grep -Eiq '(^|[[:space:]])usage:|unknown option|unknown flag|unrecognized option|invalid option' "$stderr_file"
}

classify_reviewer_attempt() {
  local exit_code="$1"
  local output_bytes="$2"
  local stderr_file="$3"
  local attempt="$4"
  local max_attempts="$5"
  local empty_retry_decision="$6"
  local retryable_decision="$7"
  local usage_retry_decision="$8"

  review_final_exit_code="$exit_code"
  review_failure_class="transient launcher failure"
  review_failure_detail="unknown launcher failure"
  review_retry_decision="no retry - completed"
  review_switch_prompt_flag=0

  if [ "$exit_code" -eq 0 ] && [ "$output_bytes" -gt 0 ]; then
    return 0
  fi

  if [ "$exit_code" -eq 0 ]; then
    review_final_exit_code=5
    if is_deterministic_setup_error "$stderr_file"; then
      review_failure_class="deterministic setup failure"
      review_failure_detail="reviewer exited 0 with empty stdout and deterministic setup stderr"
      review_retry_decision="no retry - deterministic setup failure"
    else
      review_failure_class="transient launcher failure"
      review_failure_detail="reviewer exited 0 with empty stdout"
      if [ "$attempt" -lt "$max_attempts" ]; then
        review_retry_decision="$empty_retry_decision"
      else
        review_retry_decision="no retry - empty stdout persisted"
      fi
    fi
  elif is_deterministic_setup_error "$stderr_file"; then
    review_failure_class="deterministic setup failure"
    review_failure_detail="deterministic setup failure; see stderr path"
    review_retry_decision="no retry - deterministic setup failure"
  elif is_retryable_launcher_error "$stderr_file"; then
    review_failure_class="transient launcher failure"
    review_failure_detail="retryable launcher failure; see stderr path"
    if [ "$attempt" -lt "$max_attempts" ]; then
      review_retry_decision="$retryable_decision"
      if is_prompt_flag_usage_error "$stderr_file"; then
        review_switch_prompt_flag=1
        review_retry_decision="$usage_retry_decision"
      fi
    else
      review_retry_decision="no retry - retry exhausted"
    fi
  else
    review_failure_class="non-retryable reviewer failure"
    review_failure_detail="non-retryable reviewer failure; see stderr path"
    review_retry_decision="no retry - non-retryable reviewer failure"
  fi
}
