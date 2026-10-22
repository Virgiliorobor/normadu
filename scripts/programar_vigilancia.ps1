# Registra en el Programador de tareas de Windows la corrida de scripts\vigilar_dof.py
# lunes y jueves a las 08:30 (solo con sesión iniciada; si el equipo estaba apagado, corre al encender).
# No se ejecuta solo: el owner decide correrlo. Para quitarla:
#   Unregister-ScheduledTask -TaskName "normadu vigilancia DOF" -Confirm:$false
param(
    [string]$Repo = (Split-Path -Parent $PSScriptRoot),
    [string]$Python = (Get-Command python).Source
)
$accion = New-ScheduledTaskAction -Execute $Python -Argument "-I `"$Repo\scripts\vigilar_dof.py`"" -WorkingDirectory $Repo
$cuando = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday, Thursday -At 8:30am
$ajustes = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 30)
Register-ScheduledTask -TaskName "normadu vigilancia DOF" -Action $accion -Trigger $cuando -Settings $ajustes `
    -Description "Revisa DOF (SIDOF), minisitio SAT y LeyesBiblio; escribe vigilancia\ultimo_reporte.md" -Force
