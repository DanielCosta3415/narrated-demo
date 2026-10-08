param([ValidateSet('Rollback','Uninstall')] [string]$Action, [string]$Destination = "$env:LOCALAPPDATA/NarratedDemo/runtime", [switch]$ConfirmAction)
& "$PSScriptRoot/../plugins/narrated-demo/installer/Maintain.ps1" @PSBoundParameters
