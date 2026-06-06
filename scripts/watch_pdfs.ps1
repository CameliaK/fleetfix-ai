# Watch a folder and push each new PDF into the n8n webhook (which extracts + stores it)
$folder = "C:\incoming_invoices"
if (!(Test-Path $folder)) { New-Item -ItemType Directory -Path $folder | Out-Null }

$watcher = New-Object System.IO.FileSystemWatcher $folder, "*.pdf"
$watcher.EnableRaisingEvents = $true

Register-ObjectEvent $watcher "Created" -Action {
    Start-Sleep -Milliseconds 500   # let the file finish writing
    $path = $Event.SourceEventArgs.FullPath
    Write-Host "New PDF detected: $path"
    curl.exe -F "file=@$path" http://localhost:5678/webhook/supplier-invoice
}
Write-Host "Watching $folder ... (Ctrl+C to stop)"
while ($true) { Start-Sleep 1 }