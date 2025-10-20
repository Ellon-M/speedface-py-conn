# Health Check Script for Attendance System
$LogPath = "C:\AttendanceSystem\logs\health_check.log"
$ServiceName = "AttendanceSystem"

function Write-Log {
    param([string]$Message)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$Timestamp - $Message" | Out-File -FilePath $LogPath -Append
    Write-Host $Message
}

# Check if service is running
$Service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($Service -and $Service.Status -eq 'Running') {
    Write-Log "✓ Service $ServiceName is running"
} else {
    Write-Log "✗ Service $ServiceName is not running"
    # Attempt to restart service
    Start-Service -Name $ServiceName -ErrorAction SilentlyContinue
    Write-Log "Attempted to restart $ServiceName"
}

# Check database connectivity
try {
    $ConnectionString = "server=localhost;database=attendance_db;user=attendance_user;password=StrongPassword123!;port=3306"
    $Connection = New-Object MySql.Data.MySqlClient.MySqlConnection($ConnectionString)
    $Connection.Open()
    $Connection.Close()
    Write-Log "✓ Database connection successful"
} catch {
    Write-Log "✗ Database connection failed: $($_.Exception.Message)"
}

# Check recent data
try {
    $Connection.Open()
    $Command = $Connection.CreateCommand()
    $Command.CommandText = "SELECT COUNT(*) FROM attendance WHERE created_at >= DATE_SUB(NOW(), INTERVAL 1 HOUR)"
    $RecentRecords = $Command.ExecuteScalar()
    $Connection.Close()
    Write-Log "✓ Recent records (last hour): $RecentRecords"
} catch {
    Write-Log "✗ Could not check recent records: $($_.Exception.Message)"
}