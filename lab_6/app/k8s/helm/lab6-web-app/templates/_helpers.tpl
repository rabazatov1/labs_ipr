{{- define "lab6-web-app.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "lab6-web-app.labels" -}}
app.kubernetes.io/part-of: lab6-web-app
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version | replace "+" "_" }}
{{- if .Values.environment }}
environment: {{ .Values.environment | quote }}
{{- end }}
{{- range $k, $v := .Values.labels }}
{{ $k }}: {{ $v | quote }}
{{- end }}
{{- end -}}
