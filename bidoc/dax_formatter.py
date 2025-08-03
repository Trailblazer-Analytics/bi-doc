"""
DAX Expression Formatter

This module provides functionality to format DAX expressions for better readability
in documentation.

Attribution: This formatter implements DAX formatting conventions inspired by and
compatible with DAX Formatter by SQL BI (https://github.com/sql-bi/DaxFormatter).
DAX Formatter is the industry standard for formatting DAX code and is developed by
the SQL BI team. This implementation follows similar formatting principles to ensure
consistency with established DAX coding standards.

DAX Formatter GitHub: https://github.com/sql-bi/DaxFormatter
DAX Formatter Web: https://www.daxformatter.com/
"""

import re
import signal
from typing import Optional


class DAXFormatter:
    """
    A DAX expression formatter implementing formatting conventions compatible
    with DAX Formatter by SQL BI.

    This formatter applies DAX formatting conventions to improve readability
    of DAX expressions in documentation, following standards established by
    the SQL BI DAX Formatter project.

    Attribution: Formatting conventions based on DAX Formatter by SQL BI
    (https://github.com/sql-bi/DaxFormatter), the industry standard for
    DAX code formatting.
    """

    def __init__(self, max_expression_length: int = 10000, regex_timeout: int = 5):
        """Initialize the DAX formatter with formatting rules and security limits."""
        self.max_expression_length = max_expression_length
        self.regex_timeout = regex_timeout
        # DAX functions that should be uppercase
        self.dax_functions = {
            "sum",
            "average",
            "count",
            "countrows",
            "max",
            "min",
            "calculate",
            "filter",
            "related",
            "relatedtable",
            "sumx",
            "averagex",
            "countx",
            "if",
            "switch",
            "and",
            "or",
            "not",
            "true",
            "false",
            "blank",
            "isblank",
            "isnumber",
            "istext",
            "iserror",
            "isodd",
            "iseven",
            "year",
            "month",
            "day",
            "date",
            "today",
            "now",
            "weekday",
            "yearfrac",
            "datediff",
            "dateadd",
            "format",
            "value",
            "len",
            "left",
            "right",
            "mid",
            "trim",
            "upper",
            "lower",
            "substitute",
            "concatenate",
            "exact",
            "find",
            "search",
            "replace",
            "rept",
            "var",
            "return",
            "divide",
            "roundup",
            "rounddown",
            "round",
            "ceiling",
            "floor",
            "abs",
            "sign",
            "mod",
            "quotient",
            "power",
            "exp",
            "ln",
            "log",
            "log10",
            "sqrt",
            "pi",
            "rand",
            "randbetween",
            "lookupvalue",
            "selectedvalue",
            "hasonevalue",
            "hasonefilter",
            "isfiltered",
            "iscrossfiltered",
            "allselected",
            "all",
            "values",
            "distinct",
            "earlier",
            "earliest",
            "rankx",
            "topn",
            "contains",
            "containsrow",
            "addcolumns",
            "selectcolumns",
            "summarize",
            "groupby",
            "currentgroup",
            "union",
            "intersect",
            "except",
            "crossjoin",
            "naturalinnerjoin",
            "naturalleftouterjoin",
            "generateseriesgenerate",
            "datatable",
            "row",
            "calendar",
            "calendarauto",
            "parallelperiod",
            "sameperiodlastyear",
            "datesinperiod",
            "datesbetween",
            "totalmtd",
            "totalqtd",
            "totalytd",
            "firstdate",
            "lastdate",
            "startofmonth",
            "endofmonth",
            "startofquarter",
            "endofquarter",
            "startofyear",
            "endofyear",
            "openingbalancemonth",
            "openingbalancequarter",
            "openingbalanceyear",
            "closingbalancemonth",
            "closingbalancequarter",
            "closingbalanceyear",
            "previousmonth",
            "previousquarter",
            "previousyear",
            "nextmonth",
            "nextquarter",
            "nextyear",
            "issubtotal",
            "userrelationship",
            "userelationship",
            "treatas",
            "crossfilter",
            "keepfilters",
            "removefilters",
            "allexcept",
            "ignore",
            "error",
            "iscurrent",
            "pathcontains",
            "path",
            "pathitem",
            "pathitemreverse",
            "pathlength",
            "currency",
            "fixed",
            "int",
            "trunc",
            "mround",
            "gcd",
            "lcm",
            "combin",
            "permut",
            "fact",
            "degrees",
            "radians",
            "sin",
            "cos",
            "tan",
            "asin",
            "acos",
            "atan",
            "sinh",
            "cosh",
            "tanh",
            "maxx",
            "minx",
            "productx",
            "concatenatex",
            "geomean",
            "geomeanx",
            "median",
            "medianx",
            "percentile",
            "percentilex",
            "quartile",
            "stdev",
            "stdevx",
            "stdevp",
            "stdevpx",
            "varx",
            "varp",
            "varpx",
            "beta",
            "chisq",
            "confidence",
            "expon",
            "gamma",
            "norm",
            "poisson",
            "t",
            "weibull",
            "unichar",
            "unicode",
            "code",
            "char",
            "hex2dec",
            "dec2hex",
            "bin2dec",
            "dec2bin",
            "oct2dec",
            "dec2oct",
            "base",
            "decimal",
            "dollarde",
            "dollarfr",
            "effect",
            "nominal",
            "rate",
            "nper",
            "pmt",
            "pv",
            "fv",
            "npv",
            "irr",
            "mirr",
            "xirr",
            "xnpv",
            "accrint",
            "accrintm",
            "coupdaybs",
            "coupdays",
            "coupdaysnc",
            "coupncd",
            "coupnum",
            "couppcd",
            "cumipmt",
            "cumprinc",
            "db",
            "ddb",
            "disc",
            "duration",
            "intrate",
            "mduration",
            "oddfprice",
            "oddfyield",
            "oddlprice",
            "oddlyield",
            "price",
            "pricedisc",
            "pricemat",
            "received",
            "sln",
            "syd",
            "tbilleq",
            "tbillprice",
            "tbillyield",
            "vdb",
            "yield",
            "yielddisc",
            "yieldmat",
        }

        # DAX operators
        self.operators = {"=", "<>", "<", ">", "<=", ">=", "+", "-", "*", "/", "^", "&"}

        # Keywords that should be uppercase
        self.keywords = {"and", "or", "not", "in", "var", "return"}

        # Indentation settings
        self.indent_size = 4

    def format(self, dax_expression: str) -> str:
        """
        Format a DAX expression for better readability.

        Args:
            dax_expression: The DAX expression to format

        Returns:
            Formatted DAX expression
        """
        if not dax_expression or not isinstance(dax_expression, str):
            return dax_expression

        # Input validation and security checks
        if len(dax_expression) > self.max_expression_length:
            raise ValueError(f"DAX expression too long. Maximum allowed: {self.max_expression_length} characters")

        # Remove extra whitespace and normalize
        expression = self._normalize_whitespace(dax_expression)

        # Apply basic formatting rules
        expression = self._format_functions(expression)
        expression = self._format_keywords(expression)
        expression = self._format_operators(expression)
        expression = self._format_parentheses(expression)
        expression = self._format_commas(expression)
        expression = self._format_line_breaks(expression)

        return expression.strip()

    def _normalize_whitespace(self, expression: str) -> str:
        """Normalize whitespace in the expression."""
        # Remove excessive whitespace
        expression = re.sub(r"\s+", " ", expression)
        # Remove whitespace around specific characters
        expression = re.sub(r"\s*([(),])\s*", r"\1", expression)
        return expression.strip()

    def _format_functions(self, expression: str) -> str:
        """Format DAX function names to uppercase."""

        def replace_function(match):
            func_name = match.group(1).lower()
            if func_name in self.dax_functions:
                return func_name.upper() + "("
            return match.group(0)

        # Match function names followed by opening parenthesis
        pattern = r"\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\("
        return re.sub(pattern, replace_function, expression)

    def _format_keywords(self, expression: str) -> str:
        """Format DAX keywords to uppercase."""

        def replace_keyword(match):
            keyword = match.group(1).lower()
            if keyword in self.keywords:
                return keyword.upper()
            return match.group(0)

        # Match keywords as whole words
        for keyword in self.keywords:
            pattern = r"\b(" + re.escape(keyword) + r")\b"
            expression = re.sub(
                pattern, replace_keyword, expression, flags=re.IGNORECASE
            )

        return expression

    def _format_operators(self, expression: str) -> str:
        """Add proper spacing around operators."""
        # Add spaces around operators (except inside table references)
        for op in self.operators:
            if op in ["<>", "<=", ">="]:
                # Multi-character operators
                pattern = r"\s*" + re.escape(op) + r"\s*"
                expression = re.sub(pattern, f" {op} ", expression)
            else:
                # Single character operators
                pattern = r"\s*\\" + re.escape(op) + r"\s*"
                expression = re.sub(pattern, f" {op} ", expression)

        # Clean up multiple spaces
        expression = re.sub(r"\s+", " ", expression)
        return expression

    def _format_parentheses(self, expression: str) -> str:
        """Format parentheses with proper spacing."""
        # Remove spaces before opening parenthesis (except after keywords)
        expression = re.sub(r"(?<![A-Z])\s+\(", "(", expression)

        # Add space after closing parenthesis if followed by word
        expression = re.sub(r"\)([a-zA-Z])", r") \1", expression)

        return expression

    def _format_commas(self, expression: str) -> str:
        """Format commas with proper spacing."""
        # Ensure space after comma
        expression = re.sub(r",\s*", ", ", expression)
        return expression

    def _safe_regex_sub(self, pattern: str, repl: str, text: str) -> str:
        """Perform regex substitution with timeout protection"""
        def timeout_handler(signum, frame):
            raise TimeoutError("Regex operation timed out")
        
        try:
            # Set timeout alarm (Unix-based systems only)
            if hasattr(signal, 'SIGALRM'):
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(self.regex_timeout)
            
            result = re.sub(pattern, repl, text)
            
            if hasattr(signal, 'SIGALRM'):
                signal.alarm(0)  # Cancel alarm
            
            return result
        except TimeoutError:
            # Return original text if regex times out
            return text
        except Exception:
            # Return original text if regex fails
            return text

    def _format_line_breaks(self, expression: str) -> str:
        """Add line breaks for better readability in complex expressions."""
        # This is a simplified version - more complex logic could be added

        # Break long expressions at logical points
        if len(expression) > 80:
            # Break after commas in function calls
            expression = self._safe_regex_sub(r",\s*(?=[^)]*\()", ",\\n    ", expression)

            # Break before AND/OR operators
            expression = self._safe_regex_sub(r"\s+(AND|OR)\s+", r"\\n\1 ", expression)

            # Break around VAR/RETURN
            expression = self._safe_regex_sub(r"\s+(VAR|RETURN)\s+", r"\\n\1 ", expression)

        return expression

    def format_measure(self, measure_name: str, expression: str) -> str:
        """
        Format a complete DAX measure definition.

        Args:
            measure_name: Name of the measure
            expression: DAX expression

        Returns:
            Formatted measure definition
        """
        formatted_expr = self.format(expression)

        # If the expression is complex, format it with proper indentation
        if "\\n" in formatted_expr or len(formatted_expr) > 60:
            lines = formatted_expr.split("\\n")
            indented_lines = []

            for i, line in enumerate(lines):
                if i == 0:
                    indented_lines.append(line.strip())
                else:
                    indented_lines.append(" " * self.indent_size + line.strip())

            formatted_expr = "\\n".join(indented_lines)

        return f"{measure_name} = {formatted_expr}"


def format_dax_expression(expression: str) -> str:
    """
    Convenience function to format a single DAX expression.

    Args:
        expression: DAX expression to format

    Returns:
        Formatted DAX expression
    """
    formatter = DAXFormatter()
    return formatter.format(expression)


def format_dax_measure(name: str, expression: str) -> str:
    """
    Convenience function to format a complete DAX measure.

    Args:
        name: Measure name
        expression: DAX expression

    Returns:
        Formatted measure definition
    """
    formatter = DAXFormatter()
    return formatter.format_measure(name, expression)


# Attribution comment for documentation
DAX_FORMATTER_ATTRIBUTION = """
DAX formatting in this tool is implemented using conventions compatible with
DAX Formatter by SQL BI (https://github.com/sql-bi/DaxFormatter), which is
the industry standard for DAX code formatting.

DAX Formatter is developed by the SQL BI team and provides comprehensive
formatting capabilities for DAX expressions. This implementation follows
similar principles to ensure consistency with established DAX coding standards.

For advanced DAX formatting needs, we recommend using the official DAX Formatter
tools available at:
- GitHub: https://github.com/sql-bi/DaxFormatter
- Web interface: https://www.daxformatter.com/
- VS Code extension: DAX Formatter extension by SQL BI

Special thanks to the SQL BI team for their contributions to the DAX community.
"""
