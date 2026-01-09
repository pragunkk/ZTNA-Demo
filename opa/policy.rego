package ztna

default allow = false

# Allow health checks through gateway middleware is handled in app,
# so policy focuses on protected resources.

allow {
  input.user.is_authenticated
  startswith(input.resource.path, "/apps/")
  app_id := input.resource.app
  app_allowed_for_role(app_id, input.user.role)
  device_is_trusted
  mfa_ok_for_app(app_id)
  geo_ok
}

device_is_trusted {
  input.device.device_trusted == true
}

geo_ok {
  # Demo allowlist. Extend as needed.
  input.device.geo == "IN"
} else {
  input.device.geo == "US"
}

mfa_ok_for_app(app_id) {
  # finance requires MFA
  app_id != "finance"
} else {
  input.device.mfa == true
}

app_allowed_for_role(app_id, role) {
  data.role_access[role][app_id] == true
}
