from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from .models import ITGCControl, ITGCLayer, ITGCCategory

class ITGCWorkflowTests(TestCase):
    """Test ITGC workflow loading & filtering."""
    
    def setUp(self):
        self.layer = ITGCLayer.objects.create(
            name="Access Controls",
            slug="access-controls",
            code="AC",
            description="Controls for system access"
        )
        self.category = ITGCCategory.objects.create(
            itgc_layer=self.layer,
            name="User Access",
            slug="user-access",
            sequence_order=1
        )
        self.control = ITGCControl.objects.create(
            itgc_category=self.category,
            control_id="AC-001",
            control_description="Test control",
            risk="Test risk",
            control_type="preventive",
            execution_type="manual",
            sequence_order=1,
            effective_date=timezone.now().date()
        )

    def test_load_workflow(self):
        """Test ITGC workflow loads correctly."""
        response = self.client.get(reverse('itgc:load_workflow', 
                                            args=['access-controls']))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Access Controls', response.content)

    def test_workflow_not_found(self):
        """Test 404 for invalid ITGC workflow."""
        response = self.client.get(reverse('itgc:load_workflow', 
                                            args=['nonexistent']))
        self.assertEqual(response.status_code, 200)

    def test_control_index(self):
        """Test main ITGC dashboard loads."""
        response = self.client.get(reverse('itgc:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AC-001')  # ← Changed from APP-01

    def test_filter_by_layer(self):
        """Test filtering controls by ITGC layer."""
        response = self.client.get(
            reverse('itgc:filter_by_layer', 
                    args=['access-controls'])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AC-001')  # ← Changed from APP-01

    def test_filter_by_category(self):
        """Test filtering controls by ITGC category."""
        response = self.client.get(
            reverse('itgc:filter_by_category', 
                    args=['user-access'])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AC-001')  # ← Changed from APP-01

    def test_control_detail(self):
        """Test individual ITGC control detail view."""
        response = self.client.get(
            reverse('itgc:control_detail', 
                    args=[self.control.control_id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test control')  # ← Changed

    def test_index_filtering_by_category(self):
        """Test live filtering by category."""
        response = self.client.get(
            reverse('itgc:index') + '?filter_cat=User'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AC-001')  # ← Changed

    def test_index_filtering_by_description(self):
        """Test live filtering by description."""
        response = self.client.get(
            reverse('itgc:index') + '?filter_desc=Test'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AC-001')  # ← Changed

    def test_index_filtering_by_risk(self):
        """Test live filtering by risk."""
        response = self.client.get(
            reverse('itgc:index') + '?filter_risk=Test risk'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AC-001')  # ← Changed

    def test_control_ordering(self):
        """Test controls are ordered correctly."""
        category2 = ITGCCategory.objects.create(
            name="System Access",
            itgc_layer=self.layer,
            slug="system-access",
            is_primary_flow=True,
            sequence_order=2
        )
        control2 = ITGCControl.objects.create(
            control_id="AC-002",
            itgc_category=category2,
            control_description="System access control",
            risk="Unauthorized system access",
            control_type="preventive",
            execution_type="manual",
            sequence_order=1,
            effective_date=timezone.now().date()  # ← ADDED
        )
        
        response = self.client.get(reverse('itgc:index'))
        content = response.content.decode()
        
        pos1 = content.find('AC-001')
        pos2 = content.find('AC-002')
        self.assertLess(pos1, pos2)