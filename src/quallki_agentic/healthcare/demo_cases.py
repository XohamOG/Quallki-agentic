from __future__ import annotations

HOSPITAL_DEMO_CASES = {
    "ehr_ransomware": {
        "title": "EHR ransomware behavior",
        "message": "Ransomware encryption pattern on EHR application server with unusual SMB lateral movement.",
        "source_ip": "10.20.4.18",
        "asset_type": "ehr_server",
        "contains_phi": True,
        "clinical_impact": "high",
    },
    "radiology_recon": {
        "title": "PACS reconnaissance",
        "message": "Repeated network scans against PACS and DICOM endpoints from unknown host.",
        "source_ip": "10.20.9.33",
        "asset_type": "pacs",
        "contains_phi": True,
        "clinical_impact": "medium",
    },
    "infusion_pump_access": {
        "title": "Infusion pump credential abuse",
        "message": "Multiple failed login attempts and token misuse on infusion pump management portal.",
        "source_ip": "10.20.7.51",
        "asset_type": "medical_iot",
        "contains_phi": False,
        "clinical_impact": "high",
    },
}
