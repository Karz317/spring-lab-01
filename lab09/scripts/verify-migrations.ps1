param([switch]$KeepRunning)
$ErrorActionPreference = 'Stop'
$labRoot = Split-Path $PSScriptRoot -Parent
$proofRoot = Join-Path $labRoot ('target/migration-restart-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
New-Item -ItemType Directory -Force $proofRoot | Out-Null
$dbPath = (Join-Path $proofRoot 'txlab').Replace('\','/')
$jar = Join-Path $labRoot 'target/transaction-lab09-1.0.0.jar'
if (-not (Test-Path -LiteralPath $jar)) { throw 'Build first: mvn clean verify' }
$result = @()
foreach ($stage in @('first-v2','restart-v2','upgrade-v4')) {
    $target = if ($stage -eq 'upgrade-v4') { '4' } else { '2' }
    $ddl = if ($stage -eq 'upgrade-v4') { 'validate' } else { 'none' }
    $outLog = Join-Path $proofRoot ($stage + '.log')
    $errLog = Join-Path $proofRoot ($stage + '.stderr.log')
    $argsList = @('-jar', ('"' + $jar + '"'), ('"--spring.datasource.url=jdbc:h2:file:' + $dbPath + '"'), "--spring.flyway.target=$target", "--spring.jpa.hibernate.ddl-auto=$ddl", '--server.port=8089')
    $labProcess = Start-Process -FilePath (Get-Command java).Source -ArgumentList $argsList -WindowStyle Hidden -PassThru -WorkingDirectory $labRoot -RedirectStandardOutput $outLog -RedirectStandardError $errLog
    try {
        $ready = $false
        for ($attempt=0; $attempt -lt 90; $attempt++) {
            if ($labProcess.HasExited) { throw "Application exited. Inspect $outLog and $errLog" }
            try { $null=Invoke-RestMethod 'http://127.0.0.1:8089/api/lab09/accounts' -TimeoutSec 2; $ready=$true; break } catch { Start-Sleep -Seconds 1 }
        }
        if (-not $ready) { throw 'Application did not become ready' }
        $text=Get-Content -LiteralPath $outLog -Raw
        if ($stage -eq 'restart-v2' -and $text -notmatch 'No migration necessary') { throw 'Restart unexpectedly reran migrations' }
        if ($stage -eq 'first-v2' -and $text -notmatch 'Successfully applied 2 migrations') { throw 'V1 and V2 were not applied' }
        if ($stage -eq 'upgrade-v4' -and $text -notmatch 'Successfully applied 2 migrations') { throw 'V3 and V4 were not applied' }
        $result += [pscustomobject]@{stage=$stage; target=$target; expectedApplied= $(if($stage -eq 'restart-v2'){0}else{2}); log=$outLog}
        if ($stage -eq 'upgrade-v4' -and $KeepRunning) {
            $labProcess.Id | Set-Content (Join-Path $proofRoot 'running-pid.txt')
            Write-Output "RUNNING_PID=$($labProcess.Id)"
        } else { Stop-Process -Id $labProcess.Id; $labProcess.WaitForExit() }
    } catch {
        if (-not $labProcess.HasExited) { Stop-Process -Id $labProcess.Id }
        throw
    }
}
$result | ConvertTo-Json | Set-Content -Encoding utf8 (Join-Path $proofRoot 'restart-observations.json')
Write-Output "PROOF_DIR=$proofRoot"
