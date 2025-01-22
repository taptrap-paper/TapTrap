package com.tapjacking.maltapextract.util;

public class MiscUtil {

    public static boolean isReference(String value) {
        if (value == null) {
            return false;
        }

        if (value.equals("@null")) {
            return false;
        }

        if (value.equals("@empty")) {
            return false;
        }

        if (value.startsWith("@")) {
            return true;
        }

        if (value.startsWith("?")) {
            return true;
        }

        return false;
    }
}
