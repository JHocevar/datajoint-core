use crate::types::DataJointType;
use sqlx::{Column, TypeInfo};

/// Trait for types that can be used to index columns.
///
/// Currently implemented for string (column names) and numbers (ordinals).
pub trait ColumnIndex: sqlx::ColumnIndex<sqlx::any::AnyRow> {}
impl<T> ColumnIndex for T where T: sqlx::ColumnIndex<sqlx::any::AnyRow> {}

/// Owned data about a table column.
pub struct TableColumn {
    pub ordinal: usize,
    pub name: String,
    pub type_name: DataJointType,
}

/// A reference to data about a table column.
///
/// Wraps `sqlx::any::AnyColumn`.
#[derive(Copy, Clone)]
pub struct TableColumnRef<'r> {
    column: &'r sqlx::any::AnyColumn,
}

impl<'r> TableColumnRef<'r> {
    /// Creates a new table column around a SQLx column.
    pub fn new(column: &'r sqlx::any::AnyColumn) -> Self {
        TableColumnRef { column: column }
    }

    /// Returns the integer ordinal of the column, which can be used to
    /// fetch the column in a row.
    pub fn ordinal(&self) -> usize {
        self.column.ordinal()
    }

    /// Returns the name of the column, which can be used to fetch the
    /// column in a row.
    pub fn name(&self) -> &str {
        self.column.name()
    }

    pub fn type_name(&self) -> DataJointType {
        DataJointType::from_sqlx_type_name(self.column.type_info().name())
    }

    // Converts the column reference to an owned instance for storage.
    pub fn to_owned(&self) -> TableColumn {
        TableColumn {
            ordinal: self.ordinal(),
            name: self.name().to_string(),
            type_name: self.type_name(),
        }
    }
}
