"""
AutoInsure Platform - Backend API Tests
Tests for: Auth, Dashboard, Leads, Roles, Permissions, Claims, Finance, HR, Loans, CRM, Quotations
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('EXPO_PUBLIC_BACKEND_URL', '').rstrip('/')

@pytest.fixture
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session

@pytest.fixture
def admin_token(api_client):
    """Get admin access token"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": "admin@autoinsure.com",
        "password": "Admin@123"
    })
    if response.status_code != 200:
        pytest.skip(f"Admin login failed: {response.status_code}")
    data = response.json()
    return data.get("access_token")

@pytest.fixture
def auth_headers(admin_token):
    """Headers with admin token"""
    return {"Authorization": f"Bearer {admin_token}"}


class TestAuth:
    """Authentication endpoint tests"""

    def test_login_success(self, api_client):
        """Test successful login with admin credentials"""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@autoinsure.com",
            "password": "Admin@123"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        
        data = response.json()
        assert "access_token" in data, "Missing access_token in response"
        assert "refresh_token" in data, "Missing refresh_token in response"
        assert "user" in data, "Missing user in response"
        
        user = data["user"]
        assert user["email"] == "admin@autoinsure.com"
        assert user["role"] == "super_admin"
        assert "id" in user
        assert "name" in user

    def test_login_invalid_credentials(self, api_client):
        """Test login with invalid credentials"""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@autoinsure.com",
            "password": "WrongPassword"
        })
        assert response.status_code == 401

    def test_login_missing_fields(self, api_client):
        """Test login with missing fields"""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@autoinsure.com"
        })
        assert response.status_code == 400

    def test_get_me_authenticated(self, api_client, auth_headers):
        """Test /api/auth/me with valid token"""
        response = api_client.get(f"{BASE_URL}/api/auth/me", headers=auth_headers)
        assert response.status_code == 200
        
        user = response.json()
        assert user["email"] == "admin@autoinsure.com"
        assert user["role"] == "super_admin"

    def test_get_me_unauthenticated(self, api_client):
        """Test /api/auth/me without token"""
        response = api_client.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 401


class TestDashboard:
    """Dashboard stats endpoint tests"""

    def test_dashboard_stats(self, api_client, auth_headers):
        """Test dashboard stats returns all metrics"""
        response = api_client.get(f"{BASE_URL}/api/dashboard/stats", headers=auth_headers)
        assert response.status_code == 200
        
        stats = response.json()
        # Verify all expected metrics are present
        expected_keys = [
            "total_leads", "new_leads_today", "pending_followups", "overdue_followups",
            "active_claims", "pending_rto", "pending_fitness", "total_quotations",
            "active_loans", "total_customers", "total_employees", "today_visits"
        ]
        for key in expected_keys:
            assert key in stats, f"Missing metric: {key}"
            assert isinstance(stats[key], int), f"{key} should be an integer"
        
        # Verify seeded data counts
        assert stats["total_leads"] == 12, "Should have 12 seeded leads"
        assert stats["total_customers"] == 8, "Should have 8 seeded customers"
        assert stats["total_employees"] == 5, "Should have 5 seeded employees"


class TestLeads:
    """Leads CRUD endpoint tests"""

    def test_get_leads(self, api_client, auth_headers):
        """Test GET /api/leads returns paginated leads"""
        response = api_client.get(f"{BASE_URL}/api/leads?limit=2", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert data["total"] == 12, "Should have 12 seeded leads"
        assert len(data["items"]) == 2, "Should return 2 leads with limit=2"
        
        # Verify lead structure
        lead = data["items"][0]
        assert "id" in lead
        assert "name" in lead
        assert "phone" in lead
        assert "status" in lead
        assert "priority" in lead

    def test_get_leads_with_filters(self, api_client, auth_headers):
        """Test GET /api/leads with status filter"""
        response = api_client.get(f"{BASE_URL}/api/leads?status=new", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        # All returned leads should have status 'new'
        for lead in data["items"]:
            assert lead["status"] == "new"

    def test_create_lead_and_verify(self, api_client, auth_headers):
        """Test POST /api/leads creates lead and verify with GET"""
        create_payload = {
            "name": "TEST_John Doe",
            "phone": "9999999999",
            "email": "test_john@example.com",
            "status": "new",
            "priority": "high",
            "vehicle_type": "Car",
            "insurance_type": "comprehensive"
        }
        
        # Create lead
        create_response = api_client.post(f"{BASE_URL}/api/leads", json=create_payload, headers=auth_headers)
        assert create_response.status_code == 200
        
        created_lead = create_response.json()
        assert created_lead["name"] == create_payload["name"]
        assert created_lead["phone"] == create_payload["phone"]
        assert "id" in created_lead
        
        lead_id = created_lead["id"]
        
        # Verify with GET
        get_response = api_client.get(f"{BASE_URL}/api/leads/{lead_id}", headers=auth_headers)
        assert get_response.status_code == 200
        
        fetched_lead = get_response.json()
        assert fetched_lead["name"] == create_payload["name"]
        assert fetched_lead["phone"] == create_payload["phone"]


class TestRolesAndPermissions:
    """Roles and Permissions endpoint tests"""

    def test_get_roles(self, api_client, auth_headers):
        """Test GET /api/roles returns all 19 roles"""
        response = api_client.get(f"{BASE_URL}/api/roles", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "roles" in data
        assert "role_permissions" in data
        
        roles = data["roles"]
        assert len(roles) == 19, "Should have 19 roles"
        
        # Verify key roles exist
        expected_roles = ["super_admin", "admin", "manager", "sales_executive", "telecaller", 
                         "rto_executive", "claims_executive", "accountant", "hr"]
        for role in expected_roles:
            assert role in roles, f"Missing role: {role}"

    def test_get_permissions(self, api_client, auth_headers):
        """Test GET /api/permissions returns all permissions"""
        response = api_client.get(f"{BASE_URL}/api/permissions", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "permissions" in data
        assert "total" in data
        
        # Should have 87+ permissions (request mentions 87+, code shows more)
        assert data["total"] >= 87, f"Should have at least 87 permissions, got {data['total']}"
        
        permissions = data["permissions"]
        # Verify key permissions exist
        expected_perms = ["dashboard.view", "leads.view", "leads.create", "claims.view", 
                         "finance.view", "hr.view", "users.view"]
        for perm in expected_perms:
            assert perm in permissions, f"Missing permission: {perm}"


class TestClaims:
    """Claims endpoint tests"""

    def test_get_claims(self, api_client, auth_headers):
        """Test GET /api/claims returns seeded claims"""
        response = api_client.get(f"{BASE_URL}/api/claims", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == 3, "Should have 3 seeded claims"
        
        # Verify claim structure
        if data["items"]:
            claim = data["items"][0]
            assert "id" in claim
            assert "customer_name" in claim
            assert "claim_type" in claim
            assert "claim_amount" in claim
            assert "status" in claim


class TestFinance:
    """Finance/Transactions endpoint tests"""

    def test_get_transactions(self, api_client, auth_headers):
        """Test GET /api/transactions returns seeded transactions"""
        response = api_client.get(f"{BASE_URL}/api/transactions", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "summary" in data
        assert data["total"] == 8, "Should have 8 seeded transactions"
        
        # Verify summary has income and expense
        summary = data["summary"]
        assert "income" in summary
        assert "expense" in summary
        assert summary["income"] > 0, "Should have income transactions"
        assert summary["expense"] > 0, "Should have expense transactions"


class TestHR:
    """HR/Employees endpoint tests"""

    def test_get_employees(self, api_client, auth_headers):
        """Test GET /api/employees returns seeded employees"""
        response = api_client.get(f"{BASE_URL}/api/employees", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == 5, "Should have 5 seeded employees"
        
        # Verify employee structure
        if data["items"]:
            emp = data["items"][0]
            assert "id" in emp
            assert "name" in emp
            assert "email" in emp
            assert "department" in emp
            assert "status" in emp


class TestLoans:
    """Loans endpoint tests"""

    def test_get_loans(self, api_client, auth_headers):
        """Test GET /api/loans returns seeded loans"""
        response = api_client.get(f"{BASE_URL}/api/loans", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == 3, "Should have 3 seeded loans"
        
        # Verify loan structure
        if data["items"]:
            loan = data["items"][0]
            assert "id" in loan
            assert "customer_name" in loan
            assert "loan_type" in loan
            assert "amount" in loan
            assert "status" in loan


class TestCRM:
    """CRM/Customers endpoint tests"""

    def test_get_customers(self, api_client, auth_headers):
        """Test GET /api/customers returns seeded customers"""
        response = api_client.get(f"{BASE_URL}/api/customers", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == 8, "Should have 8 seeded customers"
        
        # Verify customer structure
        if data["items"]:
            customer = data["items"][0]
            assert "id" in customer
            assert "name" in customer
            assert "phone" in customer


class TestQuotations:
    """Quotations endpoint tests"""

    def test_get_quotations(self, api_client, auth_headers):
        """Test GET /api/quotations returns seeded quotations"""
        response = api_client.get(f"{BASE_URL}/api/quotations", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == 4, "Should have 4 seeded quotations"
        
        # Verify quotation structure
        if data["items"]:
            quot = data["items"][0]
            assert "id" in quot
            assert "customer_name" in quot
            assert "premium_amount" in quot
            assert "status" in quot


class TestUsers:
    """Users endpoint tests"""

    def test_get_users(self, api_client, auth_headers):
        """Test GET /api/users returns all seeded users"""
        response = api_client.get(f"{BASE_URL}/api/users", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == 7, "Should have 7 seeded users"
        
        # Verify user structure
        if data["items"]:
            user = data["items"][0]
            assert "id" in user
            assert "email" in user
            assert "name" in user
            assert "role" in user
            # password_hash should not be in response
            assert "password_hash" not in user


# Cleanup test data
@pytest.fixture(scope="session", autouse=True)
def cleanup(request):
    """Cleanup test data after all tests"""
    def remove_test_data():
        # This will run after all tests
        pass
    request.addfinalizer(remove_test_data)
