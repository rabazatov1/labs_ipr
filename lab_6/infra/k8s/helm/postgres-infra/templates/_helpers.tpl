{{- define "postgres-infra.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "postgres-infra.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s" (include "postgres-infra.name" .) -}}
{{- end -}}
{{- end -}}

{{- define "postgres-infra.labels" -}}
app.kubernetes.io/name: {{ include "postgres-infra.name" . }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version | replace "+" "_" }}
app: postgres
{{- if .Values.environment }}
environment: {{ .Values.environment | quote }}
{{- end }}
{{- end -}}
