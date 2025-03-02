"""
Tests for the dependency injection container.
"""
import pytest
from unittest.mock import MagicMock, patch

from utils.di_container import (
    DIContainer,
    get_container,
    get_component
)


class TestComponent:
    """Test component class."""
    
    def __init__(self, name="test"):
        self.name = name


class TestDIContainer:
    """Tests for DIContainer class."""
    
    def setup_method(self):
        """Set up test."""
        # Create a container
        self.container = DIContainer()
    
    def test_register_component(self):
        """Test register_component method."""
        # Register a component
        self.container.register_component("test_component", TestComponent)
        
        # Check that component is registered
        assert "test_component" in self.container.components
        
        # Check that component factory is correct
        factory = self.container.components["test_component"]
        assert callable(factory)
        
        # Check that component is not instantiated yet
        assert "test_component" not in self.container.instances
    
    def test_register_instance(self):
        """Test register_instance method."""
        # Create an instance
        instance = TestComponent()
        
        # Register instance
        self.container.register_instance("test_instance", instance)
        
        # Check that instance is registered
        assert "test_instance" in self.container.instances
        
        # Check that instance is correct
        assert self.container.instances["test_instance"] is instance
    
    def test_get_component(self):
        """Test get_component method."""
        # Register a component
        self.container.register_component("test_component", TestComponent)
        
        # Get component
        component = self.container.get_component("test_component")
        
        # Check that component is correct
        assert isinstance(component, TestComponent)
        assert component.name == "test"
        
        # Check that component is instantiated
        assert "test_component" in self.container.instances
        
        # Get component again
        component2 = self.container.get_component("test_component")
        
        # Check that the same instance is returned
        assert component2 is component
    
    def test_get_component_with_args(self):
        """Test get_component method with args."""
        # Register a component
        self.container.register_component("test_component", TestComponent)
        
        # Get component with args
        component = self.container.get_component("test_component", "custom")
        
        # Check that component is correct
        assert isinstance(component, TestComponent)
        assert component.name == "custom"
        
        # Check that component is instantiated
        assert "test_component" in self.container.instances
        
        # Get component again
        component2 = self.container.get_component("test_component")
        
        # Check that the same instance is returned
        assert component2 is component
        assert component2.name == "custom"
    
    def test_get_component_with_kwargs(self):
        """Test get_component method with kwargs."""
        # Register a component
        self.container.register_component("test_component", TestComponent)
        
        # Get component with kwargs
        component = self.container.get_component("test_component", name="custom")
        
        # Check that component is correct
        assert isinstance(component, TestComponent)
        assert component.name == "custom"
        
        # Check that component is instantiated
        assert "test_component" in self.container.instances
        
        # Get component again
        component2 = self.container.get_component("test_component")
        
        # Check that the same instance is returned
        assert component2 is component
        assert component2.name == "custom"
    
    def test_get_component_non_singleton(self):
        """Test get_component method with non-singleton component."""
        # Register a non-singleton component
        self.container.register_component("test_component", TestComponent, singleton=False)
        
        # Get component
        component = self.container.get_component("test_component")
        
        # Check that component is correct
        assert isinstance(component, TestComponent)
        assert component.name == "test"
        
        # Check that component is not instantiated
        assert "test_component" not in self.container.instances
        
        # Get component again
        component2 = self.container.get_component("test_component")
        
        # Check that a new instance is returned
        assert component2 is not component
        assert component2.name == "test"
    
    def test_get_component_non_singleton_with_args(self):
        """Test get_component method with non-singleton component and args."""
        # Register a non-singleton component
        self.container.register_component("test_component", TestComponent, singleton=False)
        
        # Get component with args
        component = self.container.get_component("test_component", "custom")
        
        # Check that component is correct
        assert isinstance(component, TestComponent)
        assert component.name == "custom"
        
        # Check that component is not instantiated
        assert "test_component" not in self.container.instances
        
        # Get component again with different args
        component2 = self.container.get_component("test_component", "custom2")
        
        # Check that a new instance is returned
        assert component2 is not component
        assert component2.name == "custom2"
    
    def test_get_component_non_existent(self):
        """Test get_component method with non-existent component."""
        # Get non-existent component
        with pytest.raises(KeyError, match="Component not found: non_existent"):
            self.container.get_component("non_existent")
    
    def test_get_instance(self):
        """Test get_instance method."""
        # Create an instance
        instance = TestComponent()
        
        # Register instance
        self.container.register_instance("test_instance", instance)
        
        # Get instance
        instance2 = self.container.get_instance("test_instance")
        
        # Check that instance is correct
        assert instance2 is instance
    
    def test_get_instance_non_existent(self):
        """Test get_instance method with non-existent instance."""
        # Get non-existent instance
        with pytest.raises(KeyError, match="Instance not found: non_existent"):
            self.container.get_instance("non_existent")
    
    def test_has_component(self):
        """Test has_component method."""
        # Register a component
        self.container.register_component("test_component", TestComponent)
        
        # Check that component exists
        assert self.container.has_component("test_component") is True
        
        # Check that non-existent component does not exist
        assert self.container.has_component("non_existent") is False
    
    def test_has_instance(self):
        """Test has_instance method."""
        # Create an instance
        instance = TestComponent()
        
        # Register instance
        self.container.register_instance("test_instance", instance)
        
        # Check that instance exists
        assert self.container.has_instance("test_instance") is True
        
        # Check that non-existent instance does not exist
        assert self.container.has_instance("non_existent") is False


class TestContainerFunctions:
    """Tests for container functions."""
    
    def test_get_container(self):
        """Test get_container function."""
        # Get container
        container = get_container()
        
        # Check that container is a DIContainer
        assert isinstance(container, DIContainer)
        
        # Get container again
        container2 = get_container()
        
        # Check that the same container is returned
        assert container2 is container
    
    def test_get_component(self):
        """Test get_component function."""
        # Create a mock container
        mock_container = MagicMock()
        
        # Mock get_container to return the mock container
        with patch("utils.di_container.get_container", return_value=mock_container):
            # Get component
            get_component("test_component")
            
            # Check that get_component was called
            mock_container.get_component.assert_called_once_with("test_component")
    
    def test_get_component_with_args(self):
        """Test get_component function with args."""
        # Create a mock container
        mock_container = MagicMock()
        
        # Mock get_container to return the mock container
        with patch("utils.di_container.get_container", return_value=mock_container):
            # Get component with args
            get_component("test_component", "arg1", "arg2", kwarg1="value1")
            
            # Check that get_component was called
            mock_container.get_component.assert_called_once_with(
                "test_component", "arg1", "arg2", kwarg1="value1"
            )
