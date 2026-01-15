from app.models import get_all_models
import pytest


class TestModels:
	def test_get_all_models(self):
		models = get_all_models()
		model_names = [model.__name__ for model in models]

		# Check that expected models are present
		expected_models = {'Tag', 'Event'}
		for expected_model in expected_models:
			assert expected_model in model_names, f'{expected_model} not found in models'


if __name__ == '__main__':
	pytest.main([str(__file__)])
