package com.tapjacking.maltapextract;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.util.List;

/**
 * Writes animations and interpolators to a SQLite database.
 */
public class DataWriter implements AutoCloseable {

    private static final Logger logger = LoggerFactory.getLogger(DataWriter.class);

    private Connection connection;
    private final String databaseUrl;
    private final String packageName;

    public DataWriter(String packageName, String database) {
        this.packageName = packageName;
        this.databaseUrl = "jdbc:sqlite:" + database;
        connect();
        maybeCreateTables();
    }

    private void connect() {
        try {
            this.connection = DriverManager.getConnection(this.databaseUrl);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private void maybeCreateTables() {
        maybeCreateAnimationsTable();
        maybeCreateInterpolatorsTable();
    }

    private void maybeCreateAnimationsTable() {
        String createAnimTableSQL = """
            CREATE TABLE IF NOT EXISTS anim (
                id INTEGER PRIMARY KEY,
                hash TEXT,
                package_name TEXT,
                file_name TEXT,
                content TEXT
            )
        """;

        try (PreparedStatement pstmt = connection.prepareStatement(createAnimTableSQL)) {
            pstmt.execute();
        } catch (SQLException e) {
            logger.error("Error creating 'anim' table", e);
            throw new RuntimeException("Error creating 'anim' table", e);
        }
    }

    private void maybeCreateInterpolatorsTable() {
        String createInterpolatorTableSQL = """
            CREATE TABLE IF NOT EXISTS interpolator (
                id INTEGER PRIMARY KEY,
                hash TEXT,
                package_name TEXT,
                file_name TEXT,
                content TEXT
            )
        """;

        try (PreparedStatement pstmt = connection.prepareStatement(createInterpolatorTableSQL)) {
            pstmt.execute();
        } catch (SQLException e) {
            logger.error("Error creating 'interpolator' table", e);
            throw new RuntimeException("Error creating 'interpolator' table", e);
        }
    }

    public void writeAnimations(List<ResourceEntry> animations) {
        if (animations == null || animations.isEmpty()) {
            logger.warn("No animations to write to the database.");
            return;
        }

        String sql = """
        INSERT INTO anim (hash, package_name, file_name, content)
        VALUES (?, ?, ?, ?)
    """;

        try {
            connection.setAutoCommit(false); // Start transaction
            try (PreparedStatement pstmt = connection.prepareStatement(sql)) {
                for (ResourceEntry animation : animations) {
                    pstmt.setString(1, animation.getHash());
                    pstmt.setString(2, this.packageName);
                    pstmt.setString(3, animation.getFile());
                    pstmt.setString(4, animation.getXml());
                    pstmt.addBatch();
                }
                pstmt.executeBatch();
                connection.commit();
                logger.info("{} animations written to the database.", animations.size());
            }
        } catch (SQLException e) {
            try {
                connection.rollback();
                logger.error("Transaction rolled back due to error writing animations.", e);
            } catch (SQLException rollbackEx) {
                logger.error("Error during rollback", rollbackEx);
            }
            throw new RuntimeException("Error writing animations to database", e);
        } finally {
            try {
                connection.setAutoCommit(true);
            } catch (SQLException autoCommitEx) {
                logger.error("Failed to reset auto-commit mode.", autoCommitEx);
            }
        }
    }

    /**
     * Writes interpolators to the database.
     * @param interpolators The interpolators to write to the database.
     */
    public void writeInterpolators(List<ResourceEntry> interpolators) {
        String sql = """
        INSERT INTO interpolator (hash, package_name, file_name, content)
        VALUES (?, ?, ?, ?)
    """;

        try {
            connection.setAutoCommit(false); // Start transaction
            try (PreparedStatement pstmt = connection.prepareStatement(sql)) {
                for (ResourceEntry interpolator : interpolators) {
                    pstmt.setString(1, interpolator.getHash());
                    pstmt.setString(2, this.packageName);
                    pstmt.setString(3, interpolator.getFile());
                    pstmt.setString(4, interpolator.getXml());
                    pstmt.addBatch();
                }
                pstmt.executeBatch();
                connection.commit();
                logger.info("{} interpolators written to the database.", interpolators.size());
            }
        } catch (SQLException e) {
            try {
                connection.rollback();
                logger.error("Transaction rolled back due to error writing interpolators.", e);
            } catch (SQLException rollbackEx) {
                logger.error("Error during rollback", rollbackEx);
            }
            throw new RuntimeException("Error writing interpolators to database", e);
        } finally {
            try {
                connection.setAutoCommit(true);
            } catch (SQLException autoCommitEx) {
                logger.error("Failed to reset auto-commit mode.", autoCommitEx);
            }
        }
    }

    @Override
    public void close() {
        if (this.connection != null) {
            try {
                this.connection.close();
            } catch (SQLException e) {
                // Problems closing the connection is not critical, therefore we just log the error
                logger.error("Error closing the database connection", e);
            }
        }
    }
}
