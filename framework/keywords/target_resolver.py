# keywords/target_resolver.py

from __future__ import annotations

import importlib
import re
from typing import Any

from pages.base_page import BasePage


class TargetError(Exception):
    """
    Raised when an Excel Target cannot be resolved
    to a Page Object or Page Object element.
    """


PAGE_TARGET_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

ELEMENT_TARGET_PATTERN = re.compile(
    r"^([A-Za-z_][A-Za-z0-9_]*)\.([A-Za-z_][A-Za-z0-9_]*)$"
)


def get_driver(context: Any):
    """
    Get WebDriver from keyword execution context.

    Supported context forms:

        context["driver"]

    or:

        context.driver
    """

    if context is None:
        raise TargetError("TargetResolver: context is required.")

    # Dictionary-based context
    if isinstance(context, dict):
        driver = context.get("driver")

        if driver is None:
            raise TargetError("TargetResolver: context không chứa 'driver'.")

        return driver

    # Object-based context
    driver = getattr(
        context,
        "driver",
        None,
    )

    if driver is None:
        raise TargetError("TargetResolver: context không chứa driver.")

    return driver


def page_class_name(page_name: str) -> str:
    """
    Convert Excel Page Object name to class name.

    Example:
        LoginPage -> LoginPage
        ProductPage -> ProductPage
    """

    if page_name.endswith("Page"):
        return page_name

    pascal_name = re.sub(
        r"(?:^|_)([a-zA-Z0-9])",
        lambda match: match.group(1).upper(),
        page_name,
    )
    return f"{pascal_name}Page"


def page_module_name(page_name: str) -> str:
    """
    Convert Page Object class name to Python module name.

    Examples:
        LoginPage   -> pages.login_page
        ProductPage -> pages.product_page
        HomePage    -> pages.home_page
    """

    name = page_class_name(page_name)[:-4]

    if not name:
        raise TargetError(f"Target Page không hợp lệ: '{page_name}'.")

    # PascalCase -> snake_case
    snake_name = re.sub(
        r"(?<!^)(?=[A-Z])",
        "_",
        name,
    ).lower()

    return f"pages.{snake_name}_page"


def load_page_class(page_name: str):
    """
    Dynamically load Page Object class.

    Example:

        LoginPage
            ->
        pages.login_page.LoginPage
    """

    module_name = page_module_name(page_name)

    class_name = page_class_name(page_name)
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError as exc:
        raise TargetError(
            f"Không tìm thấy Page Object module "
            f"'{module_name}' cho Target '{page_name}'."
        ) from exc

    try:
        page_class = getattr(
            module,
            class_name,
        )

    except AttributeError as exc:
        raise TargetError(
            f"Module '{module_name}' không có class " f"'{class_name}'."
        ) from exc

    if not isinstance(page_class, type):
        raise TargetError(f"'{class_name}' trong '{module_name}' " f"không phải class.")

    if not issubclass(
        page_class,
        BasePage,
    ):
        raise TargetError(f"{class_name} phải kế thừa BasePage.")

    return page_class


def resolve_page(
    target: Any,
    context: Any,
) -> BasePage:
    """
    Resolve an Excel Target to a Page Object.

    Example:

        Target:
            LoginPage

        Result:
            LoginPage(driver)
    """

    if target is None:
        raise TargetError("Target không được để trống.")

    target_name = str(target).strip()

    if not target_name:
        raise TargetError("Target không được để trống.")

    if "." in target_name:
        raise TargetError(
            f"Target '{target_name}' là element Target. "
            f"resolve_page() chỉ nhận Page Target."
        )

    if not PAGE_TARGET_PATTERN.fullmatch(target_name):
        raise TargetError(f"Target Page không hợp lệ: " f"'{target_name}'.")

    driver = get_driver(context)

    page_class = load_page_class(target_name)

    try:
        return page_class(driver)
    except TypeError as exc:
        raise TargetError(
            f"Không thể khởi tạo {target_name}. "
            f"Page Object phải nhận driver trong __init__()."
        ) from exc


def resolve_element(
    target: Any,
    context: Any,
) -> tuple[BasePage, str]:
    """
    Resolve an Excel Element Target.

    Example:

        Target:
            LoginPage.Username

        Result:
            (LoginPage(driver), "Username")
    """

    if target is None:
        raise TargetError("Target không được để trống.")

    target_name = str(target).strip()

    if not target_name:
        raise TargetError("Target không được để trống.")

    match = ELEMENT_TARGET_PATTERN.fullmatch(target_name)

    if match is None:
        raise TargetError(
            f"Element Target không hợp lệ: "
            f"'{target_name}'. "
            f"Định dạng phải là PageName.ElementKey."
        )

    page_name = match.group(1)
    element_key = match.group(2)

    page = resolve_page(
        page_name,
        context,
    )

    try:
        page.locator(element_key)
    except KeyError as exc:
        raise TargetError(
            f"Element '{element_key}' không tồn tại " f"trong {page_name}.LOCATORS."
        ) from exc

    return page, element_key


def resolve_target(
    target: Any,
    context: Any,
) -> tuple[BasePage, str | None]:
    """
    Resolve either a Page Target or an Element Target.

    Page Target:

        LoginPage

    returns:

        (LoginPage(driver), None)


    Element Target:

        LoginPage.Username

    returns:

        (LoginPage(driver), "Username")
    """

    if target is None:
        raise TargetError("Target không được để trống.")

    target_name = str(target).strip()

    if not target_name:
        raise TargetError("Target không được để trống.")

    if "." not in target_name:
        page = resolve_page(
            target_name,
            context,
        )

        return page, None

    return resolve_element(
        target_name,
        context,
    )
