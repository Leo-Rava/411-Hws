from contextlib import contextmanager
import re
import sqlite3

import pytest

from boxing.models.boxers_model import (
    Boxer,
    create_boxer,
    delete_boxer,
    get_leaderboard,
    gret_boxer_by_id,
    get_boxer_by_name,
    get_weight_class,
    update_boxer_stats
)

######################################################
#
#    Fixtures
#
######################################################

def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

# Mocking the database connection for tests
@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Default return for queries
    mock_cursor.fetchall.return_value = []
    mock_cursor.commit.return_value = None

    # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object

    mocker.patch("boxer.models.boxer_model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test


######################################################
#
#    Add and delete
#
######################################################


def test_create_boxer(mock_cursor):
    """Test creating a new boxer in the catalog.

    """
    create_boxer(name="boxy", weight=130, height=155, reach=20.0, age=23)

    expected_query = normalize_whitespace("""
        INSERT INTO boxers (name, weight, height, reach, age)
        VALUES (?, ?, ?, ?, ?)
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call (second element of call_args)
    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = ("boxy", 130, 155, 20.0, 23)

    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_create_boxer_duplicate(mock_cursor):
    """Test creating a boxer with a duplicate name (should raise an error).

    """
    # Simulate that the database will raise an IntegrityError due to a duplicate entry
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: boxy")

    with pytest.raises(ValueError, match="Song with artist 'boxer_name' already exists."):
        create_boxer(name="boxy", weight=130, height=155, reach=20.0, age=23)


def test_create_boxer_invalid_weight():
    """Test error when trying to create a song with an invalid duration (e.g., negative duration)

    """
    with pytest.raises(ValueError, match=r"Invalid duration: -1 \(must be a positive integer\)."):
        create_boxer(name="boxy", weight=-1, height=155, reach=20.0, age=23)

    with pytest.raises(ValueError, match=r"Invalid duration: invalid \(must be a positive integer\)."):
        create_boxer(name="boxy", weight=-21312, height=155, reach=20.0, age=23)


def test_create_boxer_invalid_height():
    """Test error when trying to create a boxer with an invalid height (e.g., less than 0).

    """
    with pytest.raises(ValueError, match=r"Invalid height: -2 \(must be an integer greater than or equal to 1\)."):
        create_boxer(name="boxy", weight=130, height=-2, reach=20.0, age=23)

    with pytest.raises(ValueError, match=r"Invalid height: invalid \(must be an integer greater than or equal to 1\)."):
        create_boxer(name="boxy", weight=130, height="wow you sold", reach=20.0, age=23)


def test_create_boxer_invalid_reach():
    """Test error when trying to create a boxer with an invalid reach (e.g., less than 0).

    """
    with pytest.raises(ValueError, match=r"Invalid reach: -1.1 \(must be an float greater than 0\)."):
        create_boxer(name="boxy", weight=130, height=155, reach=-1.1, age=23)

    with pytest.raises(ValueError, match=r"Invalid reach: invalid \(must be an float greater than 0\)."):
        create_boxer(name="boxy", weight=130, height=155, reach="you sold again", age=23)


def test_create_boxer_invalid_age():
    """Test error when trying to create a boxer with an invalid age (e.g., between 18 and 40).

    """
    with pytest.raises(ValueError, match=r"Invalid age: 41 \(age must be an int between 18 and 40\)."):
        create_boxer(name="boxy", weight=130, height=155, reach=20.0, age=41)

    with pytest.raises(ValueError, match=r"Invalid age: 17 \(age must be an float greater than 17 and less than 41\)."):
        create_boxer(name="boxy", weight=130, height=155, reach=20.0, age=17)



def test_delete_boxer(mock_cursor):
    """Test deleting a boxer from the catalog by boxer_id.

    """
    # Simulate the existence of a boxer w/ id=1
    # We can use any value other than None
    mock_cursor.fetchone.return_value = (True)

    delete_boxer(1)

    expected_select_sql = normalize_whitespace("SELECT id FROM boxers WHERE id = ?")
    expected_delete_sql = normalize_whitespace("DELETE FROM boxers WHERE id = ?")

    # Access both calls to `execute()` using `call_args_list`
    actual_select_sql = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    actual_delete_sql = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    assert actual_select_sql == expected_select_sql, "The SELECT query did not match the expected structure."
    assert actual_delete_sql == expected_delete_sql, "The UPDATE query did not match the expected structure."

    # Ensure the correct arguments were used in both SQL queries
    expected_select_args = (1,)
    expected_delete_args = (1,)

    actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
    actual_delete_args = mock_cursor.execute.call_args_list[1][0][1]

    assert actual_select_args == expected_select_args, f"The SELECT query arguments did not match. Expected {expected_select_args}, got {actual_select_args}."
    assert actual_delete_args == expected_delete_args, f"The UPDATE query arguments did not match. Expected {expected_delete_args}, got {actual_delete_args}."


def test_delete_boxer_bad_id(mock_cursor):
    """Test error when trying to delete a non-existent song.

    """
    # Simulate that no boxer exists with the given ID
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Boxer with ID 999 not found"):
        delete_boxer(999)


######################################################
#
#    Get Boxer
#
######################################################


def test_get_boxer_by_id(mock_cursor):
    """Test getting a boxer by boxer_id.

    """
    mock_cursor.fetchone.return_value = (1, "boxy", 130, 155, 20.0, 23, False)

    result = gret_boxer_by_id(1)

    expected_result = Boxer(1, "boxy", 130, 155, 20.0, 23)

    assert result == expected_result, f"Expected {expected_result}, got {result}"

    expected_query = normalize_whitespace("SELECT id, name, weight, height, reach, age, duration FROM boxer WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = (1,)

    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_get_boxer_by_id_bad_id(mock_cursor):
    """Test error when getting a non-existent boxer.

    """
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Boxer with ID 999 not found"):
        gret_boxer_by_id(999)


def test_get_boxer_by_name(mock_cursor):
    """Test getting a boxer by a name.

    """
    mock_cursor.fetchone.return_value = (1, "boxy", 130, 155, 20.0, 23, False)

    result = get_boxer_by_name("boxy", 130, 155, 20.0, 23)

    expected_result = Boxer(1, "boxy", 130, 155, 20.0, 23)

    assert result == expected_result, f"Expected {expected_result}, got {result}"

    expected_query = normalize_whitespace("SELECT id, name, weight, height, reach, age, duration FROM boxer WHERE name = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = ("boxer_name")

    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_get_boxer_by_name_bad_name(mock_cursor):
    """Test error when getting a non-existent boxer.

    """
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Boxer with name 'boxy' not found"):
        get_boxer_by_name("boxy")


def test_get_weight_class(mock_cursor):
    """Test creating all 4 weight classes;

    """
    mock_cursor.fetchall.return_value = [
        (1, "boxy1", 204, 155, 20.0, 23, False)
        (2, "boxy2", 167, 155, 20.0, 23, False)
        (3, "boxy3", 134, 155, 20.0, 23, False)
        (4, "boxy4", 126, 155, 20.0, 23, False)
    ]

    result1 = get_weight_class(204)
    result2 = get_weight_class(167)
    result3 = get_weight_class(134)
    result4 = get_weight_class(126)

    expected_result1 = 'HEAVYWEIGHT'
    expected_result2 = 'MIDDLEWEIGHT'
    expected_result3 = 'LIGHTWEIGHT'
    expected_result4 = 'FEATHERWEIGHT'

    assert result1 == expected_result1, f"Expected {expected_result1}, got {result1}"
    assert result2 == expected_result2, f"Expected {expected_result2}, got {result2}"
    assert result3 == expected_result3, f"Expected {expected_result3}, got {result3}"
    assert result4 == expected_result4, f"Expected {expected_result4}, got {result4}"


def test_update_boxer_stats_win(mock_cursor):
    """Test whether a win is updated.
    
    """

    mock_cursor.fetchone.return_value = (1, "boxy", 130, 155, 20.0, 23, False)
    update_boxer_stats(1, "win")

    mock_cursor.execute.assert_any_call("SELECT id FROM boxers WHERE id = ?", (1,))
    mock_cursor.execute.assert_any_call("UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?", (1,))
    


    
def test_update_boxer_stats_loss(mock_cursor):
    """Test whether a loss is updated.
    
    """

    mock_cursor.fetchone.return_value = (1, "boxy", 130, 155, 20.0, 23, False)
    update_boxer_stats(1, "loss")

    mock_cursor.execute.assert_any_call("SELECT id FROM boxers WHERE id = ?", (1,))
    mock_cursor.execute.assert_any_call("UPDATE boxers SET fights = fights + 1 WHERE id = ?", (1,))
    


def test_update_boxer_stats_invalid(mock_cursor):

    mock_cursor.fetchone.return_value = None


    with pytest.raises(ValueError):
        update_boxer_stats(1, 'draw')  # 'draw' is not a valid result




def test_get_leaderboard_win(mock_cursor):
    mock_cursor.fetchall.return_value = [
        (1, "boxy1", 204, 155, 20.0, 23, False)
        (2, "boxy2", 167, 155, 20.0, 23, False)
        (3, "boxy3", 134, 155, 20.0, 23, False)
        (4, "boxy4", 126, 155, 20.0, 23, False)
    ]
    update_boxer_stats(2, "win")
    update_boxer_stats(3, "win")
    update_boxer_stats(3, "win")
    update_boxer_stats(4, "win")
    update_boxer_stats(4, "win")
    update_boxer_stats(4, "win")

    leaderboard = get_leaderboard(sort_by="wins")
    mock_cursor.execute.assert_called_once_with("""
        SELECT id, name, weight, height, reach, age, fights, wins,
               (wins * 1.0 / fights) AS win_pct
        FROM boxers
        WHERE fights > 0
        ORDER BY wins DESC
    """)

    assert len(leaderboard) == 4
    assert leaderboard[0]['name'] == 'boxy4'  # boxy4 has the most wins
    assert leaderboard[1]['name'] == 'boxy3'
    assert leaderboard[2]['name'] == 'boxy2'
    assert leaderboard[3]['name'] == 'boxy1'




def test_get_leaderboard_win_pct(mock_cursor):
    
    mock_cursor.fetchall.return_value = [
        (1, "boxy1", 204, 155, 20.0, 23, False)
        (2, "boxy2", 167, 155, 20.0, 23, False)
        (3, "boxy3", 134, 155, 20.0, 23, False)
        (4, "boxy4", 126, 155, 20.0, 23, False)
    ]
    update_boxer_stats(1, "win")
    update_boxer_stats(2, "win")
    update_boxer_stats(2, "loss")
    update_boxer_stats(3, "win")
    update_boxer_stats(3, "loss")
    update_boxer_stats(3, "loss")
    update_boxer_stats(4, "win")
    update_boxer_stats(4, "loss")
    update_boxer_stats(4, "loss")
    update_boxer_stats(4, "loss")


    leaderboard = get_leaderboard(sort_by="win_pct")


    mock_cursor.execute.assert_called_once_with("""
        SELECT id, name, weight, height, reach, age, fights, wins,
               (wins * 1.0 / fights) AS win_pct
        FROM boxers
        WHERE fights > 0
        ORDER BY win_pct DESC
    """)


    assert len(leaderboard) == 4
    assert leaderboard[0]['name'] == 'boxy1'  # boxy1 has the most win%
    assert leaderboard[1]['name'] == 'boxy2'
    assert leaderboard[2]['name'] == 'boxy3'
    assert leaderboard[3]['name'] == 'boxy4'



def test_get_leaderboard_invalid_sort():
    with pytest.raises(ValueError):
        get_leaderboard(sort_by="invalid_sort")


