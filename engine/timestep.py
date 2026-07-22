


def seconds(
    value: float,
) -> float:
    """
    Return a simulation time interval in seconds.

    Parameters
    ----------
    value : float
        Time interval (s).

    Returns
    -------
    float
        Time interval in seconds.

    Raises
    ------
    ValueError
        If the time interval is not greater than zero.

    Notes
    -----
    This function is provided for API consistency with
    minutes(), hours(), and days().

    Examples
    --------
    >>> seconds(60)
    60.0

    >>> seconds(300)
    300.0
    """

    if value <= 0.0:
        raise ValueError(
            "Time interval must be greater than zero."
        )

    return float(value)




def minutes(
    value: float,
) -> float:
    """
    Convert minutes to seconds.

    Parameters
    ----------
    value : float
        Time interval (minutes).

    Returns
    -------
    float
        Time interval in seconds.

    Raises
    ------
    ValueError
        If the time interval is not greater than zero.

    Notes
    -----
    Conversion:

        seconds = minutes × 60

    Examples
    --------
    >>> minutes(1)
    60.0

    >>> minutes(5)
    300.0

    >>> minutes(30)
    1800.0
    """

    if value <= 0.0:
        raise ValueError(
            "Time interval must be greater than zero."
        )

    return float(value) * 60.0




def hours(
    value: float,
) -> float:
    """
    Convert hours to seconds.

    Parameters
    ----------
    value : float
        Time interval (hours).

    Returns
    -------
    float
        Time interval in seconds.

    Raises
    ------
    ValueError
        If the time interval is not greater than zero.

    Notes
    -----
    Conversion:

        seconds = hours × 3600

    Examples
    --------
    >>> hours(1)
    3600.0

    >>> hours(2.5)
    9000.0

    >>> hours(24)
    86400.0
    """

    if value <= 0.0:
        raise ValueError(
            "Time interval must be greater than zero."
        )

    return float(value) * 3600.0




def days(
    value: float,
) -> float:
    """
    Convert days to seconds.

    Parameters
    ----------
    value : float
        Time interval (days).

    Returns
    -------
    float
        Time interval in seconds.

    Raises
    ------
    ValueError
        If the time interval is not greater than zero.

    Notes
    -----
    Conversion:

        seconds = days × 86400

    Examples
    --------
    >>> days(1)
    86400.0

    >>> days(0.5)
    43200.0

    >>> days(7)
    604800.0
    """

    if value <= 0.0:
        raise ValueError(
            "Time interval must be greater than zero."
        )

    return float(value) * 86400.0



import math


def simulation_steps(
    simulation_duration: float,
    time_step: float,
) -> int:
    """
    Calculate the number of simulation time steps.

    Parameters
    ----------
    simulation_duration : float
        Total simulation duration (s).

    time_step : float
        Simulation time step (s).

    Returns
    -------
    int
        Number of simulation steps.

    Raises
    ------
    ValueError
        If the simulation duration or time step is not
        greater than zero.

    Notes
    -----
    The number of steps is calculated as

        N = ceil(T / Δt)

    where

        N  = number of simulation steps

        T  = simulation duration (s)

        Δt = simulation time step (s)

    The ceiling function ensures that the complete
    simulation duration is always covered.
    """

    if simulation_duration <= 0.0:
        raise ValueError(
            "Simulation duration must be greater than zero."
        )

    if time_step <= 0.0:
        raise ValueError(
            "Time step must be greater than zero."
        )

    return math.ceil(
        simulation_duration / time_step
    )




def current_time(
    step: int,
    time_step: float,
) -> float:
    """
    Calculate the elapsed simulation time.

    Parameters
    ----------
    step : int
        Current simulation step.

    time_step : float
        Simulation time step (s).

    Returns
    -------
    float
        Elapsed simulation time (s).

    Raises
    ------
    ValueError
        If the simulation step is negative or the time
        step is not greater than zero.

    Notes
    -----
    The elapsed simulation time is calculated as

        t = n × Δt

    where

        t  = elapsed simulation time (s)

        n  = simulation step

        Δt = simulation time step (s)

    The first simulation step is step = 0,
    corresponding to t = 0 s.
    """

    if step < 0:
        raise ValueError(
            "Simulation step cannot be negative."
        )

    if time_step <= 0.0:
        raise ValueError(
            "Time step must be greater than zero."
        )

    return float(step) * time_step
