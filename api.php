<?php

$url = 'https://apisandbox.safaricom.et/mpesa/stkpush/v3/processrequest';
$data = [
    "MerchantRequestID" => "Partner name -bbab6471-a062-4886-b53a-4d67b938017e",
    "BusinessShortCode" => "1020",
    "Password" => "M2VkZGU2YWY1Y2RhMzIyOWRjMmFkMTRiMjdjOWIwOWUxZDFlZDZiNGQ0OGYyMDRiNjg0ZDZhNWM2NTQyNTk2ZA==",
    "Timestamp" => "20240918055823",
    "TransactionType" => "CustomerPayBillOnline",
    "Amount" => 20,
    "PartyA" => "251700404709",
    "PartyB" => "1020",
    "PhoneNumber" => "251700404709",
    "CallBackURL" => "https://www.myservice:8080/result",
    "AccountReference" => "Partner Unique ID",
    "TransactionDesc" => "Payment Reason",
    "ReferenceData" => [
        [
            "Key" => "ThirdPartyReference",
            "Value" => "Ref-12345"
        ]
    ]
];

$ch = curl_init($url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));

$response = curl_exec($ch);
curl_close($ch);

echo $response;


