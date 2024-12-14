import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from src.services.firestore import Parameters
from pydantic import ValidationError


class TestParametersSchema:
    def test_parameters_schema_empty(self):
        """Test de la validation du schéma des paramètres."""
        params = Parameters()
        assert not params.to_dict()

    def test_parameters_schema_str_success(self):
        """Test de la validation du schéma des paramètres avec des valeurs valides."""
        params = Parameters(**{
            "n_estimators": "499",
            "min_samples_split": "499",
            "min_samples_leaf": "499",
        })
        assert params.n_estimators == 499
        assert params.min_samples_split == 499
        assert params.min_samples_leaf == 499

    def test_parameters_schema_max_features_success(self):
        """Test de la validation du schéma des paramètres pour `max_features` avec des valeurs valides."""
        params = Parameters(max_features="sqrt")
        assert params.max_features == "sqrt"
        params = Parameters(max_features="log2")
        assert params.max_features == "log2"
        params = Parameters(max_features="auto")
        assert params.max_features == "auto"

    def test_parameters_schema_criterion_success(self):
        """Test de la validation du schéma des paramètres pour `criterion` avec des valeurs valides."""
        params = Parameters(criterion="gini")
        assert params.criterion == "gini"
        params = Parameters(criterion="entropy")
        assert params.criterion == "entropy"

    def test_parameters_schema_nestimators_failure(self):
        """Test de la validation du schéma des paramètres en cas d'erreur."""
        with pytest.raises(ValidationError) as e:
            Parameters(n_estimators=0)
        assert "ensure this value is greater than or equal to 1" in str(
            e.value)
        with pytest.raises(ValidationError) as e:
            Parameters(n_estimators=1001)
        assert "ensure this value is less than or equal to 1000" in str(
            e.value)

    def test_parameters_schema_max_depth_failure(self):
        """Test de la validation de `max_depth` pour les valeurs invalides."""
        with pytest.raises(ValidationError) as e:
            Parameters(max_depth=0)
        assert "ensure this value is greater than or equal to 1" in str(
            e.value)

    def test_parameters_schema_min_samples_split_failure(self):
        """Test de la validation de `min_samples_split` pour les valeurs invalides."""
        with pytest.raises(ValidationError) as e:
            Parameters(min_samples_split=1)
        assert "ensure this value is greater than or equal to 2" in str(
            e.value)

    def test_parameters_schema_min_samples_leaf_failure(self):
        """Test de la validation de `min_samples_leaf` pour les valeurs invalides."""
        with pytest.raises(ValidationError) as e:
            Parameters(min_samples_leaf=0)
        assert "ensure this value is greater than or equal to 1" in str(
            e.value)

    def test_parameters_schema_max_features_failure(self):
        """Test de la validation de `max_features` pour les valeurs invalides."""
        with pytest.raises(ValidationError) as e:
            Parameters(max_features="invalid_option")
        assert "value is not a valid enumeration member" in str(e.value)

    def test_parameters_schema_max_leaf_nodes_failure(self):
        """Test de la validation de `max_leaf_nodes` pour les valeurs invalides."""
        with pytest.raises(ValidationError) as e:
            Parameters(max_leaf_nodes=0)
        assert "ensure this value is greater than or equal to 1" in str(
            e.value)

    def test_parameters_schema_criterion_failure(self):
        """Test de la validation de `criterion` pour les valeurs invalides."""
        with pytest.raises(ValidationError) as e:
            Parameters(criterion="invalid_option")
        assert "value is not a valid enumeration member" in str(e.value)


class TestParametersRoute:
    @pytest.fixture
    def client(self) -> TestClient:
        """
        Test client for integration tests
        """
        from main import get_application

        app = get_application()
        return TestClient(app, base_url="http://testserver")

    @pytest.mark.asyncio
    @patch("src.services.firestore.FirestoreClient.get")
    async def test_get_parameters_success(self, mock_get: MagicMock, client: TestClient):
        """Test successful GET request to /parameters."""

        mock_parameters = {
            "n_estimators": 100,
            "max_depth": None,
            "min_samples_split": 2,
            "min_samples_leaf": 1,
            "max_features": "log2",
            "max_leaf_nodes": None,
            "criterion": "entropy"
        }
        mock_get.return_value = Parameters(**mock_parameters)

        response = client.get("/parameters")
        assert response.status_code == 200
        assert response.json() == mock_parameters
        mock_get.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.services.firestore.FirestoreClient.get")
    async def test_get_parameters_failure(self, mock_get: MagicMock, client: TestClient):
        """Test GET request to /parameters when Firestore raises an exception."""
        mock_get.side_effect = Exception("Firestore error")

        response = client.get("/parameters")
        assert response.status_code == 500
        assert "Error while fetching parameters from Firestore" in response.json()[
            "detail"]
        mock_get.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.services.firestore.FirestoreClient.put")
    async def test_put_parameters_success(self, mock_put: MagicMock, client: TestClient):
        """Test successful PUT request to /parameters."""
        mock_parameters = {
            "n_estimators": 100,
            "min_samples_split": 2,
            "min_samples_leaf": 1,
        }
        assert list(Parameters(**mock_parameters).to_dict().keys()) == [
            "n_estimators", "min_samples_split", "min_samples_leaf"]

        mock_put.return_value = (Parameters(**mock_parameters).to_dict(), 200)

        response = client.put(
            "/parameters", json=mock_parameters)
        assert response.status_code == 200
        assert response.json() == mock_parameters
