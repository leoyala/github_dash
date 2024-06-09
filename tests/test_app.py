import unittest
from unittest.mock import MagicMock, patch

from github_dash.github_stats import update_data


class TestUpdateData(unittest.TestCase):

    @patch(
        "github_dash.github_stats.get_github_commits"
    )  # Mocking the get_github_commits function
    @patch(
        "github_dash.github_stats.get_github_prs"
    )  # Mocking the get_github_prs function
    @patch(
        "github_dash.github_stats.get_github_issues"
    )  # Mocking the get_github_issues function
    @patch(
        "github_dash.github_stats.get_github_comments"
    )  # Mocking the get_github_comments function
    @patch("github_dash.github_stats.pd.read_csv")  # Mocking the pd.read_csv function
    @patch("github_dash.github_stats.pd.concat")  # Mocking the pd.concat function
    def test_update_data(
        self,
        mock_concat,
        mock_read_csv,
        mock_get_comments,
        mock_get_issues,
        mock_get_prs,
        mock_get_commits,
    ):
        """Test the 'update_data' function."""
        # Mock data
        mock_data = {
            "commits": MagicMock(),
            "prs": MagicMock(),
            "issues": MagicMock(),
            "comments": MagicMock(),
        }
        mock_get_commits.return_value = mock_data["commits"]
        mock_get_prs.return_value = mock_data["prs"]
        mock_get_issues.return_value = mock_data["issues"]
        mock_get_comments.return_value = mock_data["comments"]

        # Mock existing data
        mock_existing_data = {
            "commits": MagicMock(),
            "prs": MagicMock(),
            "issues": MagicMock(),
            "comments": MagicMock(),
        }
        mock_read_csv.side_effect = lambda file: mock_existing_data[
            file.split("_")[1].split(".")[0]
        ]

        # Mock combined data
        mock_combined_data = MagicMock()

        # Mock writing to CSV
        mock_combined_data.to_csv = MagicMock()

        # Mock lock
        mock_data_lock = MagicMock()

        with patch("github_dash.github_stats.data_lock", mock_data_lock):
            with patch(
                "github_dash.github_stats.pd.concat", return_value=mock_combined_data
            ):
                # Call the function
                result = update_data(
                    "owner/repository", "2022-01-01", "2022-12-31", "db"
                )

        # Assertions
        mock_get_commits.assert_called_once_with(
            "owner/repository", "2022-01-01", "2022-12-31"
        )
        mock_get_prs.assert_called_once_with(
            "owner/repository", "2022-01-01", "2022-12-31"
        )
        mock_get_issues.assert_called_once_with(
            "owner/repository", "2022-01-01", "2022-12-31"
        )
        mock_get_comments.assert_called_once_with(
            "owner/repository", "2022-01-01", "2022-12-31"
        )
        mock_read_csv.assert_any_call("db_commits.csv")
        mock_combined_data.to_csv.assert_any_call("db_commits.csv", index=False)
        self.assertEqual(result, mock_data)


if __name__ == "__main__":
    unittest.main()
