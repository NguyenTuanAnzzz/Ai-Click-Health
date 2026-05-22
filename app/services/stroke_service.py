from app.schemas.stroke_schema import StrokeRiskRequest, StrokeRiskResponse

def calculate_stroke_risk(data: StrokeRiskRequest) -> StrokeRiskResponse:
    # 1. Calculate BMI
    # Height in cm, weight in kg
    height_m = data.height / 100.0
    bmi = 0.0
    if height_m > 0:
        bmi = round(data.weight / (height_m ** 2), 2)
    
    # 2. Determine BMI Category (WHO Asian standard)
    if bmi < 18.5:
        bmi_category = "Thiếu cân"
    elif bmi < 23.0:
        bmi_category = "Bình thường"
    elif bmi < 25.0:
        bmi_category = "Thừa cân"
    else:
        bmi_category = "Béo phì"

    # 3. Calculate Risk Percentage
    risk_percentage = 1.0  # Base risk (1%)
    
    # Age factor
    if data.age < 40:
        risk_percentage += 0.0
    elif data.age < 55:
        risk_percentage += 5.0
    elif data.age < 70:
        risk_percentage += 12.0
    else:
        risk_percentage += 25.0
        
    # Hypertension factor
    if data.hypertension:
        risk_percentage += 15.0
        
    # Heart disease factor
    if data.heart_disease:
        risk_percentage += 18.0
        
    # Glucose level factor
    if data.glucose_level > 200.0:
        risk_percentage += 20.0
    elif data.glucose_level > 140.0:
        risk_percentage += 8.0
        
    # BMI factor
    if bmi < 18.5:
        risk_percentage += 2.0
    elif bmi < 23.0:
        risk_percentage += 0.0
    elif bmi < 25.0:
        risk_percentage += 5.0
    else:
        risk_percentage += 12.0
        
    # Smoking factor
    # Support both Vietnamese text and English values in case of standardizations
    smoking_norm = data.smoking_status.strip().lower()
    if smoking_norm in ["đã từng hút", "formerly", "formerly smoked"]:
        risk_percentage += 6.0
    elif smoking_norm in ["thường xuyên hút", "có hút", "smokes", "smoker", "currently smokes"]:
        risk_percentage += 15.0
        
    # Cap risk at 99.0%
    if risk_percentage > 99.0:
        risk_percentage = 99.0
        
    # 4. Determine Risk Category
    if risk_percentage < 10.0:
        risk_category = "Thấp"
        recommendation = (
            "Chỉ số rủi ro của bạn ở mức Thấp. Hãy duy trì chế độ ăn uống lành mạnh, "
            "tập thể dục đều đặn 150 phút/tuần, hạn chế đồ dầu mỡ và kiểm tra sức khỏe "
            "định kỳ mỗi 6 tháng để bảo vệ sức khỏe tim mạch."
        )
    elif risk_percentage <= 25.0:
        risk_category = "Trung bình"
        recommendation = (
            "Bạn có nguy cơ đột quỵ ở mức Trung bình. Cần chú ý điều chỉnh chế độ ăn uống "
            "(giảm muối, giảm đường và chất béo bão hòa), tránh stress và tuyệt đối không hút thuốc. "
            "Nên tầm soát đột quỵ định kỳ và tham khảo ý kiến bác sĩ nếu có bất kỳ triệu chứng mệt mỏi kéo dài nào."
        )
    else:
        risk_category = "Cao"
        recommendation = (
            "CẢNH BÁO: Chỉ số rủi ro đột quỵ của bạn đang ở mức CAO. Bạn cần đến gặp bác sĩ chuyên khoa "
            "tim mạch/thần kinh ngay để kiểm tra huyết áp, đường huyết và nhận phác đồ điều trị phù hợp. "
            "Hãy ghi nhớ quy tắc BEFAST để phát hiện sớm các dấu hiệu đột quỵ cấp tính."
        )

    return StrokeRiskResponse(
        bmi=bmi,
        bmi_category=bmi_category,
        risk_percentage=round(risk_percentage, 1),
        risk_category=risk_category,
        recommendation=recommendation
    )
