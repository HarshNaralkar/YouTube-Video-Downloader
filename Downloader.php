<?php
function getDownloadFolder() {
    $os = PHP_OS_FAMILY;
    
    if ($os === "Windows") {
        return getenv("USERPROFILE") . "\\Downloads";
    } elseif ($os === "Darwin") {  // macOS
        return getenv("HOME") . "/Downloads";
    } elseif ($os === "Linux") {
        return getenv("HOME") . "/Downloads";
    } else {
        return getenv("HOME");  // Fallback to home directory
    }
}

function sanitizeFilename($filename) {
    return preg_replace('/[<>:"\/\\|?*\'\s]/', '', $filename);
}

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['videoUrl'])) {
    $videoUrl = $_POST['videoUrl'];
    $outputFolder = getDownloadFolder();

    // Extract title from URL for file naming
    $title = sanitizeFilename(parse_url($videoUrl, PHP_URL_QUERY));
    $videoFile = $outputFolder . "/" . $title . ".mp4";
    $audioFile = $outputFolder . "/" . $title . ".m4a";

    // Define a unique name with timestamp for the final output file
    $finalTitle = "Downloadedfile";
    $timestamp = date("Ymd_His");
    $finalOutput = $outputFolder . "/" . $finalTitle . "_" . $timestamp . ".mp4";

    try {
        // Download video
        $videoCommand = "yt-dlp -f bestvideo -o " . escapeshellarg($videoFile) . " " . escapeshellarg($videoUrl);
        shell_exec($videoCommand);

        // Download audio
        $audioCommand = "yt-dlp -f bestaudio -o " . escapeshellarg($audioFile) . " " . escapeshellarg($videoUrl);
        shell_exec($audioCommand);

        // Merge video and audio with ffmpeg
        $ffmpegCommand = "ffmpeg -i " . escapeshellarg($videoFile) . " -i " . escapeshellarg($audioFile) .
                         " -c:v copy -c:a aac -strict experimental " . escapeshellarg($finalOutput);
        shell_exec($ffmpegCommand);

        // Clean up: Remove separate audio and video files
        unlink($videoFile);
        unlink($audioFile);

        // Optionally set the final file as hidden (Windows only)
        if (strtoupper(substr(PHP_OS, 0, 3)) === 'WIN') {
            shell_exec("attrib +h " . escapeshellarg($finalOutput));
        }

        // Respond with success
        echo json_encode([
            'status' => 'success',
            'message' => 'Your video has been downloaded successfully!',
            'file' => $finalOutput
        ]);
    } catch (Exception $e) {
        // Respond with error
        echo json_encode([
            'status' => 'error',
            'message' => $e->getMessage()
        ]);
    }
} else {
    // Render HTML page if GET request
    echo file_get_contents("Index.html");
}
?>
