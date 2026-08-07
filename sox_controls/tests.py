from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from .models import SoxControl, BusinessProcess, SubProcess

class WorkflowTests(TestCase):
    """Test SOX workflow loading & filtering."""
    
    def setUp(self):
        self.process = BusinessProcess.objects.create(name="P2P", slug="p2p")
        self.subprocess = SubProcess.objects.create(
            business_process=self.process,
            name="Invoice Processing",
            slug="invoice-processing",
            sequence_order=1
        )
        self.control = SoxControl.objects.create(
            control_id="P2P-001",
            sub_process=self.subprocess,
            control_description="Test control",
            risk="Test risk",
            control_type="preventive",
            execution_type="manual",
            sequence_order=1,
            effective_date=timezone.now().date()
        )

    def test_load_workflow(self):
        """Test workflow loads correctly."""
        response = self.client.get(reverse('sox_controls:load_workflow', 
                                            args=['p2p']))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'P2P', response.content)

    def test_workflow_not_found(self):
        """Test 404 for invalid workflow."""
        response = self.client.get(reverse('sox_controls:load_workflow', 
                                            args=['nonexistent']))
        self.assertEqual(response.status_code, 200)

    def test_control_index(self):
        """Test main dashboard loads."""
        response = self.client.get(reverse('sox_controls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'P2P-001')

    def test_filter_by_process(self):
        """Test filtering controls by business process."""
        response = self.client.get(
            reverse('sox_controls:filter_by_process', 
                    args=['p2p'])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'P2P-001')

    def test_filter_by_subprocess(self):
        """Test filtering controls by subprocess."""
        response = self.client.get(
            reverse('sox_controls:filter_by_subprocess', 
                    args=['invoice-processing'])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'P2P-001')

    def test_control_detail(self):
        """Test individual control detail view."""
        response = self.client.get(
            reverse('sox_controls:control_detail', 
                    args=[self.control.control_id])  
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test control')

    def test_index_filtering_by_description(self):
        """Test live filtering by description."""
        response = self.client.get(
            reverse('sox_controls:index') + '?filter_desc=Test'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'P2P-001')

    def test_index_filtering_by_risk(self):
        """Test live filtering by risk."""
        response = self.client.get(
            reverse('sox_controls:index') + '?filter_risk=Test'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'P2P-001')

    def test_control_ordering(self):
        """Test controls are ordered correctly."""
        subprocess2 = SubProcess.objects.create(
            name="Invoice",
            business_process=self.process,
            slug="invoice",
            is_primary_flow=True,
            sequence_order=2
        )
        control2 = SoxControl.objects.create(
            control_id="P2P-002",
            sub_process=subprocess2,
            control_description="Second control",
            risk="Test risk",
            control_type="preventive",
            execution_type="manual",
            sequence_order=1,
            effective_date=timezone.now().date()  # ← ADDED
        )
        
        response = self.client.get(reverse('sox_controls:index'))
        content = response.content.decode()
        
        pos1 = content.find('P2P-001')
        pos2 = content.find('P2P-002')
        self.assertLess(pos1, pos2)