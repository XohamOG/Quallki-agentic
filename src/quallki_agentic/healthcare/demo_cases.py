from __future__ import annotations

HOSPITAL_DEMO_CASES = {
    "ehr_ransomware": {
        "title": "EHR ransomware behavior",
        "message": "Ransomware encryption pattern on EHR application server with unusual SMB lateral movement.",
        "source_ip": "10.20.4.18",
        "asset_type": "ehr_server",
        "contains_phi": True,
        "clinical_impact": "high",
        "logs": [
            "2026-08-20T10:00:01Z EHR-SRV-01 smb lateral movement from 10.20.4.18",
            "2026-08-20T10:00:04Z EHR-SRV-01 powershell shadow copy deletion",
            "2026-08-20T10:00:09Z EHR-SRV-01 ransomware encrypting patient records",
        ],
    },
    "radiology_recon": {
        "title": "PACS reconnaissance",
        "message": "Repeated network scans against PACS and DICOM endpoints from unknown host.",
        "source_ip": "10.20.9.33",
        "asset_type": "pacs",
        "contains_phi": True,
        "clinical_impact": "medium",
        "logs": [
            "2026-08-20T11:14:02Z PACS-01 port scan from 10.20.9.33",
            "2026-08-20T11:14:05Z PACS-01 DICOM endpoint enumeration",
            "2026-08-20T11:14:09Z PACS-01 repeated network probe detected",
        ],
    },
    "infusion_pump_access": {
        "title": "Infusion pump credential abuse",
        "message": "Multiple failed login attempts and token misuse on infusion pump management portal.",
        "source_ip": "10.20.7.51",
        "asset_type": "medical_iot",
        "contains_phi": False,
        "clinical_impact": "high",
        "logs": [
            "2026-08-20T12:20:01Z PUMP-MGMT failed login for svc_pump from 10.20.7.51",
            "2026-08-20T12:20:03Z PUMP-MGMT failed login for svc_pump from 10.20.7.51",
            "2026-08-20T12:20:06Z PUMP-MGMT credential token misuse detected",
        ],
    },
}
