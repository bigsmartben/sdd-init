"COMMAND: Get-Content docs/test-reports/order/2026-11-05-review.md"
Get-Content docs/test-reports/order/2026-11-05-review.md
"COMMAND: compare SHA256 against evidence/review-raw.txt and review-chk008-raw.txt"
$initial = Get-Content evidence/review-raw.txt
$incremental = Get-Content evidence/review-chk008-raw.txt
$files = @('src/__init__.py','src/order_service.py','src/storage.py','src/ui.py','tests/test_order.py','checks/acceptance.py','checks/runtime_details.py','runtime.json')
foreach ($file in $files) {
  $actual = (Get-FileHash -Algorithm SHA256 $file).Hash
  $suffix = $file.Replace('/', '\')
  $escaped = [regex]::Escape($suffix)
  $old = @($initial | Where-Object { $_ -match "^SHA256\s+([A-F0-9]{64})\s+.*$escaped$" })
  $new = @($incremental | Where-Object { $_ -match "^SHA256\s+([A-F0-9]{64})\s+.*$escaped$" })
  $oldHash = if ($old.Count -eq 1 -and $old[0] -match '^SHA256\s+([A-F0-9]{64})') { $Matches[1] } else { 'MISSING' }
  $newHash = if ($new.Count -eq 1 -and $new[0] -match '^SHA256\s+([A-F0-9]{64})') { $Matches[1] } else { 'NOT_CAPTURED' }
  "$file actual=$actual initial=$oldHash initial_match=$($actual -eq $oldHash) incremental=$newHash incremental_match=$(if ($newHash -eq 'NOT_CAPTURED') {'not captured'} else {$actual -eq $newHash})"
}
