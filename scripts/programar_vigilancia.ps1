# Registra en el Programador de tareas de Windows, lunes y jueves a las 08:30 (solo con sesión iniciada;
# si el equipo estaba apagado, corre al encender):
#   1. git pull --ff-only del clon local de solo lectura (si existe), desde GitHub;
#   2. scripts\vigilar_dof.py, que escribe vigilancia\ultimo_reporte.md.
# Sin -I en Python: pdfminer.six está en el site-packages del usuario y -I lo excluye.
# Para quitarla:
#   Unregister-ScheduledTask -TaskName "normadu vigilancia DOF" -Confirm:$false
param(
    [string]$Repo = (Split-Path -Parent $PSScriptRoot),
    [string]$Python = (Get-Command python).Source,
    [string]$Clon = "C:\Users\Jaime V. Rob\Dev\normadu",
    [string]$Git = (Get-Command git).Source
)
$acciones = @()
if (Test-Path -LiteralPath (Join-Path $Clon ".git")) {
    $acciones += New-ScheduledTaskAction -Execute $Git -Argument "-C `"$Clon`" pull --ff-only --quiet"
}
$acciones += New-ScheduledTaskAction -Execute $Python -Argument "`"$Repo\scripts\vigilar_dof.py`"" -WorkingDirectory $Repo
$cuando = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday, Thursday -At 8:30am
$ajustes = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 30)
Register-ScheduledTask -TaskName "normadu vigilancia DOF" -Action $acciones -Trigger $cuando -Settings $ajustes `
    -Description "Actualiza el clon de solo lectura y revisa DOF (SIDOF), minisitio SAT y LeyesBiblio; escribe vigilancia\ultimo_reporte.md" -Force
