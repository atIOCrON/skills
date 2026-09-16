die() {
  echo "error: $*" >&2
  exit 1
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || die "$1 not found on PATH"
}

load_remote() {
  local remote="$1" address remainder
  address="$(git remote get-url "$remote" 2>/dev/null)" || die "unknown remote: $remote"

  case "$address" in
    *://*)
      remainder="${address#*://}"
      remainder="${remainder#*@}"
      PROVIDER_HOST="${remainder%%/*}"
      PROVIDER_PATH="${remainder#*/}"
      ;;
    *@*:*)
      remainder="${address#*@}"
      PROVIDER_HOST="${remainder%%:*}"
      PROVIDER_PATH="${remainder#*:}"
      ;;
    *)
      die "remote $remote is not a hosted Git URL: $address"
      ;;
  esac

  PROVIDER_PATH="${PROVIDER_PATH#/}"
  PROVIDER_PATH="${PROVIDER_PATH%.git}"
  PROVIDER_URL="$address"
  [ -n "$PROVIDER_HOST" ] && [ -n "$PROVIDER_PATH" ] || die "cannot parse remote: $address"
}

require_sha() {
  case "$1" in
    ''|*[!0-9a-fA-F]*) die "$2 must be a hexadecimal SHA" ;;
  esac
}
