import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_health_endpoint() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["app_name"] == "NyayaLens"

@pytest.mark.asyncio
async def test_full_document_workflow() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Upload valid legal text document
        sample_doc = (
            "SECTION 1: TITLE AND PARTIES\n"
            "This Agreement is between Acme Corp and John Doe.\n\n"
            "SECTION 11.2: TERMINATION\n"
            "In the event of voluntary resignation, Employee shall provide ninety (90) days prior written notice.\n\n"
            "SECTION 8.1: NON-COMPETE\n"
            "Employee shall not engage in competing business for 12 months post-termination.\n"
        )
        files = {"file": ("employment_agreement_v1.txt", sample_doc.encode("utf-8"), "text/plain")}
        upload_res = await client.post("/api/v1/documents", files=files)
        assert upload_res.status_code == 201
        doc_meta = upload_res.json()
        doc_id = doc_meta["document_id"]

        # 2. Get clauses
        clauses_res = await client.get(f"/api/v1/documents/{doc_id}/clauses")
        assert clauses_res.status_code == 200
        clauses = clauses_res.json()
        assert len(clauses) > 0

        # 3. Get obligations
        obl_res = await client.get(f"/api/v1/documents/{doc_id}/obligations")
        assert obl_res.status_code == 200

        # 4. Get summary
        sum_res = await client.get(f"/api/v1/documents/{doc_id}/summary")
        assert sum_res.status_code == 200
        assert "Employment" in sum_res.json()["document_type"]

        # 5. Q&A Grounded Query
        qa_res = await client.post(
            f"/api/v1/documents/{doc_id}/ask",
            json={"question": "What happens if I resign?", "plain_language_mode": "standard"},
        )
        assert qa_res.status_code == 200
        qa_data = qa_res.json()
        assert qa_data["insufficient_evidence"] is False
        assert "90 days" in qa_data["answer"] or "ninety" in qa_data["answer"]
        assert len(qa_data["citations"]) > 0
        cached_qa_res = await client.post(
            f"/api/v1/documents/{doc_id}/ask",
            json={"question": "What happens if I resign?", "plain_language_mode": "standard"},
        )
        assert cached_qa_res.json() == qa_data

        # 6. Q&A Insufficient Evidence query
        unknown_res = await client.post(
            f"/api/v1/documents/{doc_id}/ask",
            json={"question": "What is the policy regarding pet dog food in the kitchen?", "plain_language_mode": "standard"},
        )
        assert unknown_res.status_code == 200
        assert unknown_res.json()["insufficient_evidence"] is True

        # 7. Checklist generation
        check_res = await client.post(f"/api/v1/documents/{doc_id}/checklist")
        assert check_res.status_code == 200
        assert len(check_res.json()) > 0
        cached_check_res = await client.post(f"/api/v1/documents/{doc_id}/checklist")
        assert cached_check_res.json() == check_res.json()

        # 8. Lawyer Preparation questions
        lawyer_res = await client.post(f"/api/v1/documents/{doc_id}/lawyer-questions")
        assert lawyer_res.status_code == 200
        assert len(lawyer_res.json()) > 0
        cached_lawyer_res = await client.post(f"/api/v1/documents/{doc_id}/lawyer-questions")
        assert cached_lawyer_res.json() == lawyer_res.json()

        # 9. Comparison: Upload Version B
        sample_doc_v2 = (
            "SECTION 1: TITLE AND PARTIES\n"
            "This Agreement is between Acme Corp and John Doe.\n\n"
            "SECTION 11.2: TERMINATION\n"
            "In the event of voluntary resignation, Employee shall provide thirty (30) days prior written notice.\n"
        )
        files_v2 = {"file": ("employment_agreement_v2.txt", sample_doc_v2.encode("utf-8"), "text/plain")}
        upload_v2 = await client.post("/api/v1/documents", files=files_v2)
        doc_v2_id = upload_v2.json()["document_id"]

        compare_res = await client.post(
            "/api/v1/compare",
            json={"doc_a_id": doc_id, "doc_b_id": doc_v2_id},
        )
        assert compare_res.status_code == 200
        comp_data = compare_res.json()
        assert len(comp_data["semantic_changes"]) > 0
